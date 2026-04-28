#!/bin/bash
# Resets the production database using AWS ECS
# NOTE: The script assumes you are logged in with terraform

# usage: reset_db aws_profile aws_region

if [[ "$#" != 2 ]]; then
    echo "usage: reset_db aws_profile aws_region"
    exit 1
fi

aws_profile=$1
aws_region=$2
echo "using account: $1 in $2"
echo "Note: make sure you logged in with terraform CLI using 'terraform login'"

set -e
cd ./database/terraform
terraform init
EPA_MONGODB_HOSTNAME=$(terraform output -raw mongo_db_cluster_dns_name)

# Get variables for ecs command
cluster_name=$(terraform output -raw mongo_db_cluster_name)
service_name=$(terraform output -raw first_mongodb_service)

# Move to ./database
cd ../
echo "Updating $cluster_name using serivce $service_name"

# Get Task ARN for one of the nodes in the cluster
task_arn=$(aws ecs list-tasks \
    --cluster "$cluster_name" \
    --service-name "$service_name" \
    --desired-status RUNNING \
    --query 'taskArns[0]' --output text \
    --region "$aws_region" --profile "$aws_profile")

echo "Target Task ARN: $task_arn"
if [ "$task_arn" == "None" ] || [ -z "$task_arn" ]; then
    echo "No RUNNING task found yet"
    exit 1
fi

echo "Clearing DB"
aws ecs execute-command \
    --region "$aws_region" \
    --profile "$aws_profile" \
    --cluster "$cluster_name" \
    --task "$task_arn" \
    --container "mongo" \
    --interactive \
    --command "sh -c '
    
        export EPA_MONGODB_USERNAME=\$MONGO_INITDB_ROOT_USERNAME
        export EPA_MONGODB_PASSWORD=\$MONGO_INITDB_ROOT_PASSWORD
        
        # make mongosh run small for ecs storage size
        export NODE_OPTIONS=\"--max-old-space-size=128\"
    
        mongosh \"mongodb+srv://\${EPA_MONGODB_USERNAME}:\${EPA_MONGODB_PASSWORD}@\"$EPA_MONGODB_HOSTNAME\"/epa_database?tls=false\" \
          --quiet \
          --norc \
          --eval \"db.dropDatabase(); quit()\"
          
    '"
echo "Done"

REQ_B64=$(base64 -w 0 ./requirements.txt)
SCRIPT_B64=$(base64 -w 0 ./init.py)
CONFIG_B64=$(base64 -w 0 ./config.json)

echo "Resetting DB"
aws ecs execute-command \
    --region "$aws_region" \
    --profile "$aws_profile" \
    --cluster "$cluster_name" \
    --task "$task_arn" \
    --container "mongo" \
    --interactive \
    --command "sh -c '

    # Move needed files over
    echo $REQ_B64 | base64 -d > /tmp/requirements.txt
    echo $SCRIPT_B64 | base64 -d > /tmp/init.py
    echo $CONFIG_B64 | base64 -d > /tmp/config.json

    # Setup env variables
    export EPA_MONGODB_HOSTNAME=\"$EPA_MONGODB_HOSTNAME\"
    export EPA_MONGODB_PORT=27017
    export EPA_MONGODB_DATABASE_NAME=\"epa_database\"
    export EPA_MONGODB_USERNAME=\$MONGO_INITDB_ROOT_USERNAME
    export EPA_MONGODB_PASSWORD=\$MONGO_INITDB_ROOT_PASSWORD

    # Install script dependencies
    apt update && apt install -y python3 python3.10-venv
    python3 -m venv /tmp/.venv
    /tmp/.venv/bin/pip install -r /tmp/requirements.txt > /dev/null

    # Run
    cd /tmp
    /tmp/.venv/bin/python3 /tmp/init.py --is-cluster

    # Finish
    echo SUCCESS_TOKEN: Database initialized
    '"
    
echo "Done"