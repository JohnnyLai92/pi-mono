@echo off
node "%~dp0node_modules\tsx\dist\cli.mjs" "%~dp0packages\coding-agent\src\cli.ts" %*
