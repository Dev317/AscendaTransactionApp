variable "github_token" {
  description = "Github access token"
  type        = string
  default    = ""
}

variable "waftech_region" {
  description = "Wafter region name"
  type = string
  default = ""
}

variable "waftech_branch" {
  description = "Repo branch"
  type = string
  default = ""
}
