/* UNCOMMENT ME IF USING DEV EC2 INSTANCE
output "ec2_sg" {
  value = aws_security_group.ec2_sg
}
*/

output "efs_sg" {
  value = aws_security_group.efs_sg
}

output "mongo_ecs_tasks_sg" {
  value = aws_security_group.mongo_ecs_tasks_sg
}

output "ecs_mongo_task_role" {
  value = aws_iam_role.ecs_mongo_task_role
}

output "ec2_instance_profile" {
  value = aws_iam_instance_profile.ecs_node_profile
}
output "ecs_task_execution_role" {
  value = aws_iam_role.ecs_task_execution_role
}