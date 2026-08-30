# API doc (version 0.9.4a)

**The CodeTabs API was closed since 2026-06-30**，this API can not use anymore！

## **Description**

\- Tool for counting lines of code from github/gitlab repositories.
\- Max Repo size: 500 mb, greater repos will not work.
\- File max size for upload 200mb.
\- Can select a branch different than master using &branch=branchName.
\- Can ignore files or directories writing them separated by commas in the ignoreBox.
\- Can edit the colors of the segments by clicking on any point of it. Segment will randomly change color as it is clicked.
\- Default colors are the same as github.
\- Limit: 1 request every 5 seconds. Once reached subsequent requests will result in error 429 (too many requests) until your quota is cleared.

**Endpoint - Get Lines of Code from GitHub repo**
This endpoint retrieves LOC from any github repo based on programming language.

**curl Request:** add -L flag
`curl -L https://api.codetabs.com/v1/loc?source=username/reponame`
**http Request:**
`GET https://api.codetabs.com/v1/loc?github=username/reponame`
`GET https://api.codetabs.com/v1/loc?gitlab=username/reponame`

**Select branch**
If you want a different branch than master
`https://api.codetabs.com/v1/loc?SOURCE=USERNAME/REPONAME&branch=branchName`
**Ignore files or directories**
Can ignore files or directories using param ignored
`https://api.codetabs.com/v1/loc?SOURCE=USERNAME/REPONAME&ignored=DIRNAME1,DIRNAME2,FILENAME`
**example:**
`https://api.codetabs.com/v1/loc?github=jolav/betazone`
`https://api.codetabs.com/v1/loc?gitlab=jolav/chuletas`
`https://api.codetabs.com/v1/loc?github=imageMagick/imageMagick&branch=gh-pages`
`https://api.codetabs.com/v1/loc?github=jolav/betazone&ignored=www,main.go`

**response:**

```json
[{
  "language": "JavaScript",
  "files": 1,
  "lines": 176,
  "blanks": 14,
  "comments": 6,
  "linesOfCode": 156
},   
... more languages
{
  "language": "Total",
  "files": 8,
  "lines": 921,
  "blanks": 148,
  "comments": 46,
  "linesOfCode": 743
}]
```

**Endpoint - Get Lines of Code from an zipped directory**
This endpoint retrieves LOC from any zipped directory

**http Request:** `POST https://api.codetabs.com/v1/loc`
**parameter: Form Data**
`Content-Disposition: form-data; name="inputFile"; filename="yourRarZipFolder.zip"`
**response:** Same as Endpoint - Get Lines of Code from any zipped Project
