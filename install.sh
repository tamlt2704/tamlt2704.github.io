#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# Developer Setup Tool for Fresh Debian
# Uses whiptail for interactive selection
# =============================================================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_ok()   { echo -e "${GREEN}[✓]${NC} $1"; }
log_info() { echo -e "${YELLOW}[+]${NC} $1"; }

# Check if whiptail is available
if ! command -v whiptail &>/dev/null; then
    echo "Installing whiptail..."
    sudo apt-get update && sudo apt-get install -y whiptail
fi

# =============================================================================
# Selection UI
# =============================================================================

CHOICES=$(whiptail --title "Debian Developer Setup" \
    --checklist "Select tools to install (SPACE to toggle, ENTER to confirm):" 30 70 20 \
    "essentials"    "Build tools, git, curl, wget, htop, tree, jq" ON \
    "python"        "Python 3 + pip + venv" ON \
    "uv"            "uv - Fast Python package manager" ON \
    "node"          "Node.js (via nvm) + npm" ON \
    "java"          "OpenJDK 17 + Maven" OFF \
    "docker"        "Docker CE + Compose plugin" ON \
    "vscode"        "Visual Studio Code" ON \
    "ollama"        "Ollama - Local LLM runner" OFF \
    "n8n"           "n8n - Workflow automation (Docker)" OFF \
    "rust"          "Rust (via rustup)" OFF \
    "go"            "Go (latest from official tarball)" OFF \
    "neovim"        "Neovim (latest stable)" OFF \
    "tmux"          "tmux terminal multiplexer" OFF \
    "zsh"           "Zsh + Oh My Zsh" OFF \
    "postgresql"    "PostgreSQL client + server" OFF \
    "redis"         "Redis server" OFF \
    "nginx"         "Nginx web server" OFF \
    "ssh-server"    "OpenSSH server" OFF \
    "firewall"      "UFW firewall (deny incoming, allow SSH)" OFF \
    "fonts"         "Developer fonts (FiraCode, JetBrains Mono)" OFF \
    3>&1 1>&2 2>&3) || { echo "Cancelled."; exit 0; }

# =============================================================================
# Preview or Install
# =============================================================================

if whiptail --title "Preview or Install?" \
    --yesno "Do you want to PREVIEW commands first?\n\n(Yes = show commands only, No = install now)" 10 60; then
    PREVIEW=true
else
    PREVIEW=false
fi

# =============================================================================
# Installation functions
# =============================================================================

install_essentials() {
    if $PREVIEW; then
        echo "sudo apt-get update"
        echo "sudo apt-get install -y build-essential git curl wget htop tree jq unzip zip \\"
        echo "  ca-certificates gnupg lsb-release software-properties-common \\"
        echo "  apt-transport-https net-tools dnsutils"
    else
        sudo apt-get update
        sudo apt-get install -y build-essential git curl wget htop tree jq unzip zip \
            ca-certificates gnupg lsb-release software-properties-common \
            apt-transport-https net-tools dnsutils
        log_ok "Essentials installed"
    fi
}

install_python() {
    if $PREVIEW; then
        echo "sudo apt-get install -y python3 python3-pip python3-venv python3-dev"
    else
        sudo apt-get install -y python3 python3-pip python3-venv python3-dev
        log_ok "Python installed"
    fi
}

install_uv() {
    if $PREVIEW; then
        echo 'curl -LsSf https://astral.sh/uv/install.sh | sh'
    else
        if command -v uv &>/dev/null; then
            log_ok "uv already installed"
        else
            curl -LsSf https://astral.sh/uv/install.sh | sh
            log_ok "uv installed"
        fi
    fi
}

install_node() {
    if $PREVIEW; then
        echo 'curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash'
        echo 'nvm install --lts'
    else
        if command -v node &>/dev/null; then
            log_ok "Node already installed: $(node --version)"
        else
            curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
            export NVM_DIR="$HOME/.nvm"
            # shellcheck disable=SC1091
            [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
            nvm install --lts
            log_ok "Node.js installed via nvm"
        fi
    fi
}

install_java() {
    if $PREVIEW; then
        echo "sudo apt-get install -y openjdk-17-jdk maven"
    else
        sudo apt-get install -y openjdk-17-jdk maven
        log_ok "Java 17 + Maven installed"
    fi
}

install_docker() {
    if $PREVIEW; then
        echo "sudo install -m 0755 -d /etc/apt/keyrings"
        echo "curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg"
        echo "sudo chmod a+r /etc/apt/keyrings/docker.gpg"
        echo 'echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null'
        echo "sudo apt-get update"
        echo "sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin"
        echo 'sudo usermod -aG docker $USER'
    else
        if command -v docker &>/dev/null; then
            log_ok "Docker already installed"
        else
            sudo install -m 0755 -d /etc/apt/keyrings
            curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
            sudo chmod a+r /etc/apt/keyrings/docker.gpg
            local arch
            arch=$(dpkg --print-architecture)
            local codename
            codename=$(. /etc/os-release && echo "$VERSION_CODENAME")
            echo "deb [arch=${arch} signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian ${codename} stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            sudo apt-get update
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
            sudo usermod -aG docker "$USER"
            log_ok "Docker installed (log out and back in for group)"
        fi
    fi
}

install_vscode() {
    if $PREVIEW; then
        echo "curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg"
        echo 'echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list > /dev/null'
        echo "sudo apt-get update"
        echo "sudo apt-get install -y code"
    else
        if command -v code &>/dev/null; then
            log_ok "VS Code already installed"
        else
            curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg
            echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list > /dev/null
            sudo apt-get update
            sudo apt-get install -y code
            log_ok "VS Code installed"
        fi
    fi
}

install_ollama() {
    if $PREVIEW; then
        echo 'curl -fsSL https://ollama.com/install.sh | sh'
    else
        if command -v ollama &>/dev/null; then
            log_ok "Ollama already installed"
        else
            curl -fsSL https://ollama.com/install.sh | sh
            log_ok "Ollama installed"
        fi
    fi
}

install_n8n() {
    if $PREVIEW; then
        echo "docker pull n8nio/n8n"
    else
        if docker image inspect n8nio/n8n &>/dev/null 2>&1; then
            log_ok "n8n already pulled"
        else
            docker pull n8nio/n8n
            log_ok "n8n Docker image pulled"
        fi
    fi
}

install_rust() {
    if $PREVIEW; then
        echo 'curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y'
    else
        if command -v rustc &>/dev/null; then
            log_ok "Rust already installed"
        else
            curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
            log_ok "Rust installed"
        fi
    fi
}

install_go() {
    if $PREVIEW; then
        echo 'GO_VERSION=$(curl -s https://go.dev/VERSION?m=text | head -1)'
        echo 'curl -fsSL "https://go.dev/dl/${GO_VERSION}.linux-amd64.tar.gz" -o /tmp/go.tar.gz'
        echo "sudo rm -rf /usr/local/go"
        echo "sudo tar -C /usr/local -xzf /tmp/go.tar.gz"
        echo 'echo "export PATH=\$PATH:/usr/local/go/bin" >> ~/.bashrc'
    else
        if command -v go &>/dev/null; then
            log_ok "Go already installed: $(go version)"
        else
            local go_version
            go_version=$(curl -s https://go.dev/VERSION?m=text | head -1)
            curl -fsSL "https://go.dev/dl/${go_version}.linux-amd64.tar.gz" -o /tmp/go.tar.gz
            sudo rm -rf /usr/local/go
            sudo tar -C /usr/local -xzf /tmp/go.tar.gz
            rm /tmp/go.tar.gz
            echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
            log_ok "Go installed"
        fi
    fi
}

install_neovim() {
    if $PREVIEW; then
        echo "curl -fsSL https://github.com/neovim/neovim/releases/latest/download/nvim-linux-x86_64.tar.gz -o /tmp/nvim.tar.gz"
        echo "sudo tar -C /usr/local --strip-components=1 -xzf /tmp/nvim.tar.gz"
    else
        if command -v nvim &>/dev/null; then
            log_ok "Neovim already installed"
        else
            curl -fsSL https://github.com/neovim/neovim/releases/latest/download/nvim-linux-x86_64.tar.gz -o /tmp/nvim.tar.gz
            sudo tar -C /usr/local --strip-components=1 -xzf /tmp/nvim.tar.gz
            rm /tmp/nvim.tar.gz
            log_ok "Neovim installed"
        fi
    fi
}

install_tmux() {
    if $PREVIEW; then
        echo "sudo apt-get install -y tmux"
    else
        sudo apt-get install -y tmux
        log_ok "tmux installed"
    fi
}

install_zsh() {
    if $PREVIEW; then
        echo "sudo apt-get install -y zsh"
        echo 'sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended'
        echo 'chsh -s $(which zsh)'
    else
        sudo apt-get install -y zsh
        sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
        chsh -s "$(which zsh)"
        log_ok "Zsh + Oh My Zsh installed"
    fi
}

install_postgresql() {
    if $PREVIEW; then
        echo "sudo apt-get install -y postgresql postgresql-client"
    else
        sudo apt-get install -y postgresql postgresql-client
        log_ok "PostgreSQL installed"
    fi
}

install_redis() {
    if $PREVIEW; then
        echo "sudo apt-get install -y redis-server"
    else
        sudo apt-get install -y redis-server
        log_ok "Redis installed"
    fi
}

install_nginx() {
    if $PREVIEW; then
        echo "sudo apt-get install -y nginx"
    else
        sudo apt-get install -y nginx
        log_ok "Nginx installed"
    fi
}

install_ssh_server() {
    if $PREVIEW; then
        echo "sudo apt-get install -y openssh-server"
        echo "sudo systemctl enable --now ssh"
    else
        sudo apt-get install -y openssh-server
        sudo systemctl enable --now ssh
        log_ok "SSH server installed and enabled"
    fi
}

install_firewall() {
    if $PREVIEW; then
        echo "sudo apt-get install -y ufw"
        echo "sudo ufw default deny incoming"
        echo "sudo ufw default allow outgoing"
        echo "sudo ufw allow ssh"
        echo "sudo ufw --force enable"
    else
        sudo apt-get install -y ufw
        sudo ufw default deny incoming
        sudo ufw default allow outgoing
        sudo ufw allow ssh
        sudo ufw --force enable
        log_ok "UFW configured"
    fi
}

install_fonts() {
    if $PREVIEW; then
        echo "sudo apt-get install -y fonts-firacode fonts-jetbrains-mono"
    else
        sudo apt-get install -y fonts-firacode fonts-jetbrains-mono
        log_ok "Developer fonts installed"
    fi
}

# =============================================================================
# Run selected installations
# =============================================================================

if $PREVIEW; then
    echo ""
    echo "========================================="
    echo " COMMANDS THAT WOULD BE EXECUTED:"
    echo "========================================="
    echo ""
fi

for choice in $CHOICES; do
    item=$(echo "$choice" | tr -d '"')

    if $PREVIEW; then
        echo "--- [$item] ---"
    else
        log_info "Installing: $item"
    fi

    case "$item" in
        essentials)   install_essentials ;;
        python)       install_python ;;
        uv)           install_uv ;;
        node)         install_node ;;
        java)         install_java ;;
        docker)       install_docker ;;
        vscode)       install_vscode ;;
        ollama)       install_ollama ;;
        n8n)          install_n8n ;;
        rust)         install_rust ;;
        go)           install_go ;;
        neovim)       install_neovim ;;
        tmux)         install_tmux ;;
        zsh)          install_zsh ;;
        postgresql)   install_postgresql ;;
        redis)        install_redis ;;
        nginx)        install_nginx ;;
        ssh-server)   install_ssh_server ;;
        firewall)     install_firewall ;;
        fonts)        install_fonts ;;
    esac

    if $PREVIEW; then echo ""; fi
done

if $PREVIEW; then
    echo "========================================="
    echo " Run again and choose 'No' to install."
    echo "========================================="
else
    echo ""
    log_ok "All done! You may need to log out and back in for some changes to take effect."
fi