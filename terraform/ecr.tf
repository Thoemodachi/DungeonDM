resource "aws_ecr_repository" "backend" {
  name = "${var.project_name}-backend"
  image_scanning_configuration { scan_on_push = true }
  tags = { Name = "${var.project_name}-backend" }
}

resource "aws_ecr_repository" "frontend" {
  name = "${var.project_name}-frontend"
  image_scanning_configuration { scan_on_push = true }
  tags = { Name = "${var.project_name}-frontend" }
}

output "backend_ecr"  { value = aws_ecr_repository.backend.repository_url }
output "frontend_ecr" { value = aws_ecr_repository.frontend.repository_url }
