#!/bin/bash

# Install dependencies
npm install

# Add custom aliases
cat >> ~/.bashrc << 'EOF'

# Custom aliases
alias dev="npm run dev"
alias build="npm run build"
alias deploy="npm run deploy"
alias gs="git status"
alias gp="git push"
alias gc="git commit"
alias gd="git diff"
EOF
