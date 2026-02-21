#!/bin/bash
# Take environment variables from ../.env and 
# define them as Terraform environment variables
# usage: source source_tf_env.sh

ENV_FILE_LOCATION="../.env"

while IFS= read -r line; do
    export TF_VAR_$line
done < $ENV_FILE_LOCATION

export TF_IN_AUTOMATION=true
    
