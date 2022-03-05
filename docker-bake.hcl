# see https://www.postgresql.org/support/versioning/ for Postgresql lifecycle policy

variable "PGBACKUP_VERSION" {
    default = "1.0.1"
}

group "default" {
	targets = ["14-alpine", "13-alpine", "12-alpine", "11-alpine", "10-alpine"]
}

target "14-alpine" {
	dockerfile = "Dockerfile"
	platforms = ["linux/amd64", "linux/arm64", "linux/arm/v7"]
    args = {"PGVERSION" = "14"}
    tags = ["johnivore/postgres-backup:14-alpine-${PGBACKUP_VERSION}", "johnivore/postgres-backup:14-alpine-latest"]
}

target "13-alpine" {
	dockerfile = "Dockerfile"
	platforms = ["linux/amd64", "linux/arm64", "linux/arm/v7"]
    args = {"PGVERSION" = "13"}
    tags = ["johnivore/postgres-backup:13-alpine-${PGBACKUP_VERSION}", "johnivore/postgres-backup:13-alpine-latest"]
}

target "12-alpine" {
	dockerfile = "Dockerfile"
	platforms = ["linux/amd64", "linux/arm64", "linux/arm/v7"]
    args = {"PGVERSION" = "12"}
    tags = ["johnivore/postgres-backup:12-alpine-${PGBACKUP_VERSION}", "johnivore/postgres-backup:12-alpine-latest"]
}

target "11-alpine" {
	dockerfile = "Dockerfile"
	platforms = ["linux/amd64", "linux/arm64", "linux/arm/v7"]
    args = {"PGVERSION" = "11"}
    tags = ["johnivore/postgres-backup:11-alpine-${PGBACKUP_VERSION}", "johnivore/postgres-backup:11-alpine-latest"]
}

target "10-alpine" {
	dockerfile = "Dockerfile"
	platforms = ["linux/amd64", "linux/arm64", "linux/arm/v7"]
    args = {"PGVERSION" = "10"}
    tags = ["johnivore/postgres-backup:10-alpine-${PGBACKUP_VERSION}", "johnivore/postgres-backup:10-alpine-latest"]
}
