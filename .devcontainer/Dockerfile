ARG VARIANT="3.9"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

LABEL maintainer "Peter Schmalfeldt peter@findbycolor.com"
LABEL version="1.0"
LABEL description="Proof of Concept"
LABEL vendor="Find By Color"

WORKDIR /fbc

# Add non-root user
ARG USERNAME=findbycolor
RUN groupadd --gid 1000 $USERNAME && useradd --uid 1000 --gid 1000 -m $USERNAME

## Make sure to reflect new user in PATH
ENV PATH="/home/${USERNAME}/.local/bin:${PATH}"
USER $USERNAME

# Support Signed Commit Messages
RUN sudo apt-get update && sudo apt-get install gnupg2 -y

# Install helpful scripts
RUN sudo apt-get install exa wget -y

# Copy Shell Scripts to Container
RUN mkdir -p /usr/local/lib/sfcc-remote
COPY docker-assets/scripts/* /usr/local/lib/sfcc-remote
RUN sudo chmod +x /usr/local/lib/sfcc-remote/*

# Copy / Replace Dot Files
COPY docker-assets/dotfiles/.* /home/findbycolor

# Configure Git to use Global .gitattributes to prevent EOL and Whitespace Conflicts
RUN su findbycolor -c "git config --global core.attributesfile /home/findbycolor/.gitattributes"
RUN su findbycolor -c "git config --global pull.rebase false"

# Install ZSH Plugins
RUN su findbycolor -c "git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting"
RUN su findbycolor -c "git clone https://github.com/zsh-users/zsh-autosuggestions ~/.oh-my-zsh/custom/plugins/zsh-autosuggestions"

RUN apt-get update && apt-get install -y build-essential curl software-properties-common git libgl1 && rm -rf /var/lib/apt/lists/*



## Pip dependencies
# Upgrade pip
RUN pip install --upgrade pip

# Install Production Dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Install Development Dependencies
COPY requirements-dev.txt /tmp/requirements-dev.txt
RUN pip install -r /tmp/requirements-dev.txt && rm /tmp/requirements-dev.txt

# Persist Bash History
RUN SNIPPET="export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" \
    && mkdir /commandhistory \
    && touch /commandhistory/.bash_history \
    && chown -R node /commandhistory \
    && echo $SNIPPET >> /home/node/.bashrc

# Add Support for Live Share
RUN wget -O ~/vsls-reqs https://raw.githubusercontent.com/MicrosoftDocs/live-share/master/scripts/linux-prereqs.sh \
    --no-check-certificate \
    && chmod +x ~/vsls-reqs \
    && ~/vsls-reqs


RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8501
