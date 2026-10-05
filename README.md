# github-repo-management 
 
Central request-as-code automation for GitHub organization repository creation. 
 
## Repository naming 
`Product-purpose-service`, normalized to lowercase. 
Example: `edgeai-object-detection-api` 
 
## Working branch naming 
`username/Purpose/jira-ticket` 
Example: `neha/object-detection/EDGE-102` 
 
## Branch flow 
`username/Purpose/jira-ticket` -> PR -> `dev` -> PR -> `main` 
 
## Request a new repository 
1. Create a working branch in this management repository. 
2. Add `requests/<product>-<purpose>-<service>.yml`. 
3. Add product, purpose, service, description and visibility. 
4. Open a pull request to `main`. 
5. Wait for validation and required approval. 
6. Merge the PR. 
7. GitHub Actions creates the repository and `dev` branch automatically. 
 
Never commit credentials or tokens to this repository.
