# Store OpenAI key. Note: Terraform state will contain this value.
# Prefer supplying it at apply time and using a remote state backend with encryption.
resource "aws_ssm_parameter" "openai_api_key" {
  name   = "/${var.project_name}/openai/api_key"
  type   = "SecureString"
  value  = var.openai_api_key
  tags   = { Name = "${var.project_name}-openai-key" }
}
