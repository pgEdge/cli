
apt --version
rc=$?
if [ "$rc" == "0" ]; then
  keyring_gpg=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
  sudo rm -rf $keyring_gpg
  curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o $keyring_gpg \
    && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
      sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
      sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
  sudo apt-get update
  sudo apt-get install -y nvidia-container-toolkit
else
  curl -s -L https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo | \
    sudo tee /etc/yum.repos.d/nvidia-container-toolkit.repo
  sudo yum install -y nvidia-container-toolkit
fi

## generate CDI specification
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
nvidia-ctk cdi list

#podman run --rm --device nvidia.com/gpu=all --security-opt=label=disable ubuntu nvidia-smi -L


