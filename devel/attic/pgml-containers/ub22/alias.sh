alias pbld="podman build -t pgedgeml --force-rm  ."

## WARNING:  Our sample db trust's connections without autrhetication so we only allow u
##              connecting from localhost
alias prun="podman run -ti -p 127.0.0.1:65432:5432 --rm --device=nvidia.com/gpu=0 pgedgeml"

