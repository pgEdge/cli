
export pgeMdDir=~/dev/pgedge/cli/help
export nc=../out/posix/pgedge
export output_dir=../docs

modules=(ace cluster db localhost service spock um)
commands=(setup upgrade-cli)

mkdir -p "$output_dir"

parse_to_markdown(){
   sed -r 's/\x1B\[[0-9;]*[mGKH]//g; /^(SYNOPSIS|POSITIONAL ARGUMENTS|DESCRIPTION|FLAGS|COMMANDS)/s/^/## /'
}

get_module_commands() {
  local module="$1"
  local module_file="$output_dir/functions/$module.md"
  local cmds=()
  if [[ -f "$module_file" ]]; then
    local in_commands=0
    while IFS= read -r line; do
      if [[ "$line" =~ COMMAND\ is\ one\ of\ the\ following: ]]; then
        in_commands=1
        continue
      fi
      if [[ $in_commands -eq 1 ]]; then
        [[ -z "$line" ]] && break
        if [[ "$line" =~ ^[[:space:]]*([a-zA-Z0-9_-]+)[[:space:]]*# ]]; then
          cmd="${BASH_REMATCH[1]}"
          cmds+=("$cmd")
        fi
      fi
    done < "$module_file"
  fi
  echo "${cmds[@]}"
}


write_help() {
  # Generate help for a command or module (and its subcommands)
  local module="$1"
  $nc $module --help | parse_to_markdown > "$output_dir/functions/$module.md";
  
  # Parse the generated module help file to extract subcommands (if they exist)
  module_commands=($(get_module_commands "$module"))
  if [ ${#module_commands[@]} -gt 0 ]; then
    echo "Found sub commands for module '$module': ${module_commands[*]}"
  else
    return
  fi
  
  # Generate help for each command in the module
  for cmd in "${module_commands[@]}"; do
    local fname="${module}-$(echo "$cmd" | tr ' ' '-').md"
    echo "Generating help for module '$module', command '$cmd' -> $fname"

    if ! $nc $module $cmd --help | parse_to_markdown > "$output_dir/functions/$fname"; then
      echo "ERROR: Failed to generate help for module '$module', command '$cmd'" >&2
    fi
  done
}

index() {
  local index_file="$output_dir/cli_functions.md"
  echo "# CLI Functions" > "$index_file"
  echo "" >> "$index_file"

  # Loop through all stand-alone commands and generate index entries
  echo "## standalone commands" >> "$index_file"
  echo "" >> "$index_file"
  echo "| Command | Description |" >> "$index_file"
  echo "|---------|-------------|" >> "$index_file"
  

  for command in "${commands[@]}"; do
      command_file="$output_dir/functions/${command}.md"
      if [[ -f "$command_file" ]]; then
        desc=$(awk '
          BEGIN { found=0 }
          /^## DESCRIPTION/ { found=1; next }
          found && /^[[:space:]]*[^[:space:]]/ { gsub(/^[ \t]+|[ \t]+$/, "", $0); print $0; exit }
        ' "$command_file")
        
        echo "| [\`$command\`](functions/$command.md) | $desc |" >> "$index_file"
      fi
  done

  echo "" >> "$index_file"

  for module in "${modules[@]}"; do
    echo "## $module module commands" >> "$index_file"
    echo "" >> "$index_file"
    echo "| Command | Description |" >> "$index_file"
    echo "|---------|-------------|" >> "$index_file"
    # Parse the -module.md file to extract commands and descriptions
    module_file="$output_dir/functions/${module}.md"
    awk -v module="$module" '
      BEGIN { in_commands=0 }
      /COMMAND is one of the following:/ { in_commands=1; next }
      in_commands && /^[[:space:]]*$/ { exit }
      in_commands && /^[[:space:]]*[^[:space:]]/ {
      # Match: <cmd>   # <desc>
      split($0, parts, "#")
      cmd=parts[1]
      gsub(/^[ \t]+|[ \t]+$/, "", cmd)
      desc=parts[2]
      gsub(/^[ \t]+|[ \t]+$/, "", desc)
      if (cmd != "") {
        printf "| [`%s %s`](functions/%s-%s.md) | %s |\n", module, cmd, module, cmd, desc
      }
      }
    ' "$module_file" >> "$index_file"
    echo "" >> "$index_file"

  done
}

############## MAINLINE ############################
if [ $# -ne 1 ]; then
  echo "ERROR: must be one 'module' parameter"
  exit 1
fi

m=$1
if [ "$m" == "all" ]; then
  echo "Generating help for all modules..."
  echo "Removing existing help files..."
  rm -f $output_dir/functions/*

  # Loop through all modules and generate help
  for module in "${modules[@]}"; do
    write_help "$module"
  done

  # Loop through all stand-alone commands and generate help
  echo "Generating help for all standalone commands..."
  for command in "${commands[@]}"; do
    write_help "$command"
  done

  index
elif [ "$m" == "index" ]; then
  index
else
  echo "Generating help for module '$m'..."

  # Check if the module or command is valid
  if [[ ! " ${modules[@]} " =~ " ${m} " && ! " ${commands[@]} " =~ " ${m} " ]]; then
    echo "ERROR: '$m' is not a valid module or command. Valid modules are: ${modules[*]}. Valid commands are: ${commands[*]}"
    exit 1
  fi
  write_help "$m"
fi
