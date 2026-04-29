#!/usr/bin/env bash
set -euo pipefail

# create-release-packages.sh (workflow-local)

# Build Spec Kit template release archives for each supported AI assistant and script type.

# Usage: .github/workflows/scripts/create-release-packages.sh <version>

# Version argument should include leading 'v'.

# Optionally set AGENTS and/or SCRIPTS env vars to limit what gets built.

# AGENTS : space or comma separated subset of: claude gemini copilot (default: all)

# SCRIPTS : space or comma separated subset of: sh ps (default: both)

# Examples:

# AGENTS=claude SCRIPTS=sh $0 v0.2.0

# AGENTS="copilot,gemini" $0 v0.2.0

# SCRIPTS=ps $0 v0.2.0

if [[ $# -ne 1 ]]; then

  echo "Usage: $0 <version-with-v-prefix>" >&2

  exit 1

fi

NEW_VERSION="$1"

if [[ ! $NEW_VERSION =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-.*)?$ ]]; then

  echo "Version must look like v0.0.0" >&2

  exit 1

fi

# Remove 'v' prefix for package naming
PACKAGE_VERSION=${NEW_VERSION#v}

echo "Building release packages for $NEW_VERSION (packages will use $PACKAGE_VERSION)"

# Create and use .genreleases directory for all build artifacts
GENRELEASES_DIR=".genreleases"
mkdir -p "$GENRELEASES_DIR"
rm -rf "$GENRELEASES_DIR"/* || true

rewrite_paths() {
  # Only rewrite top-level paths (memory/, scripts/, templates/) that appear at
  # the start of a path, not nested inside other paths like .../project-context/memory/.
  # Match when preceded by: start-of-line, whitespace, backtick, quote, paren, or standalone /
  sed -E \
    -e 's@(^|[[:space:]"`'\''(])(/?)memory/@\1.specify/memory/@g' \
    -e 's@(^|[[:space:]"`'\''(])(/?)scripts/@\1.specify/scripts/@g' \
    -e 's@(^|[[:space:]"`'\''(])(/?)templates/@\1.specify/templates/@g'
}

# Agent-specific path mappings for project rules, skills, and config directories
agent_skills_dir() {
  local agent=$1
  case $agent in
    claude)         echo ".claude/skills" ;;
    windsurf)       echo ".windsurf/skills" ;;
    cursor-agent)   echo ".cursor/skills" ;;
    codex)          echo ".codex/skills" ;;
    copilot)        echo ".github/skills" ;;
    gemini)         echo ".gemini/skills" ;;
    qwen)           echo ".qwen/skills" ;;
    opencode)       echo ".opencode/skills" ;;
    kilocode)       echo ".kilocode/skills" ;;
    *)              echo ".specify/skills" ;;
  esac
}

agent_rules_file() {
  local agent=$1
  case $agent in
    claude)         echo "CLAUDE.md" ;;
    windsurf)       echo ".windsurfrules" ;;
    cursor-agent)   echo ".cursorrules" ;;
    codex)          echo "AGENTS.md" ;;
    copilot)        echo ".github/copilot-instructions.md" ;;
    gemini)         echo "GEMINI.md" ;;
    qwen)           echo "QWEN.md" ;;
    opencode)       echo "AGENTS.md" ;;
    kilocode)       echo ".kilocode/rules/project-rules.md" ;;
    *)              echo ".windsurfrules" ;;
  esac
}

agent_rules_dir() {
  local agent=$1
  case $agent in
    claude)         echo ".claude/rules" ;;
    windsurf)       echo ".windsurf/rules" ;;
    cursor-agent)   echo ".cursor/rules" ;;
    codex)          echo ".codex/rules" ;;
    copilot)        echo ".github/rules" ;;
    gemini)         echo ".gemini/rules" ;;
    qwen)           echo ".qwen/rules" ;;
    opencode)       echo ".opencode/rules" ;;
    kilocode)       echo ".kilocode/rules" ;;
    *)              echo ".specify/rules" ;;
  esac
}

agent_config_dir() {
  local agent=$1
  case $agent in
    claude)         echo ".claude/" ;;
    windsurf)       echo ".windsurf/" ;;
    cursor-agent)   echo ".cursor/" ;;
    codex)          echo ".codex/" ;;
    copilot)        echo ".github/" ;;
    gemini)         echo ".gemini/" ;;
    qwen)           echo ".qwen/" ;;
    opencode)       echo ".opencode/" ;;
    kilocode)       echo ".kilocode/" ;;
    *)              echo ".windsurf/" ;;
  esac
}

generate_commands() {

  local agent=$1 ext=$2 arg_format=$3 output_dir=$4 script_variant=$5

  mkdir -p "$output_dir"

  for template in templates/commands/*.md; do

    [[ -f "$template" ]] || continue

    local name description script_command agent_script_command body

    name=$(basename "$template" .md)

    # Normalize line endings

    file_content=$(tr -d '\r' < "$template")

    # Extract description and script command from YAML frontmatter

    description=$(printf '%s\n' "$file_content" | awk '/^description:/ {sub(/^description:[[:space:]]*/, ""); print; exit}')

    script_command=$(printf '%s\n' "$file_content" | awk -v sv="$script_variant" '/^[[:space:]]*'"$script_variant"':[[:space:]]*/ {sub(/^[[:space:]]*'"$script_variant"':[[:space:]]*/, ""); print; exit}')

    if [[ -z $script_command ]]; then

      echo "Warning: no script command found for $script_variant in $template" >&2

      script_command="(Missing script command for $script_variant)"

    fi

    # Extract agent_script command from YAML frontmatter if present
    agent_script_command=$(printf '%s\n' "$file_content" | awk '
      /^agent_scripts:$/ { in_agent_scripts=1; next }
      in_agent_scripts && /^[[:space:]]*'"$script_variant"':[[:space:]]*/ {
        sub(/^[[:space:]]*'"$script_variant"':[[:space:]]*/, "")
        print
        exit
      }
      in_agent_scripts && /^[a-zA-Z]/ { in_agent_scripts=0 }
    ')

    # Replace {SCRIPT} placeholder with the script command

    body=$(printf '%s\n' "$file_content" | sed "s|{SCRIPT}|${script_command}|g")

    # Replace {AGENT_SCRIPT} placeholder with the agent script command if found
    if [[ -n $agent_script_command ]]; then
      body=$(printf '%s\n' "$body" | sed "s|{AGENT_SCRIPT}|${agent_script_command}|g")
    fi

    # Remove the scripts: and agent_scripts: sections from frontmatter while preserving YAML structure

    body=$(printf '%s\n' "$body" | awk '

    /^---$/ { print; if (++dash_count == 1) in_frontmatter=1; else in_frontmatter=0; next }

    in_frontmatter && /^scripts:$/ { skip_scripts=1; next }

    in_frontmatter && /^agent_scripts:$/ { skip_scripts=1; next }

    in_frontmatter && /^[a-zA-Z].*:/ && skip_scripts { skip_scripts=0 }

    in_frontmatter && skip_scripts && /^[[:space:]]/ { next }

    { print }

')

    # Rewrite paths for packaged output (scripts/ -> .specify/scripts/, etc.)

    body=$(printf '%s\n' "$body" | rewrite_paths)

    # Apply other substitutions

    local skills_dir rules_file config_dir
    skills_dir=$(agent_skills_dir "$agent")
    rules_file=$(agent_rules_file "$agent")
    config_dir=$(agent_config_dir "$agent")

    body=$(printf '%s\n' "$body" | sed \
      -e "s|{ARGS}|$arg_format|g" \
      -e "s|__AGENT__|$agent|g" \
      -e "s|__AGENT_SKILLS_DIR__|$skills_dir|g" \
      -e "s|__AGENT_RULES_FILE__|$rules_file|g" \
      -e "s|__AGENT_CONFIG_DIR__|$config_dir|g" )

    case $ext in

      toml)

        body=$(printf '%s\n' "$body" | sed 's/\\/\\\\/g')

        { echo "description = \"$description\""; echo; echo "prompt = \"\"\""; echo "$body"; echo "\"\"\""; } > "$output_dir/$name.$ext" ;;

      md)

        echo "$body" > "$output_dir/$name.$ext" ;;

      agent.md)

        echo "$body" > "$output_dir/$name.$ext" ;;

    esac

  done

}

generate_copilot_prompts() {
  local agents_dir=$1 prompts_dir=$2
  mkdir -p "$prompts_dir"

  # Generate a .prompt.md file for each .agent.md file
  for agent_file in "$agents_dir"/*.agent.md; do
    [[ -f "$agent_file" ]] || continue

    local basename=$(basename "$agent_file" .agent.md)
    local prompt_file="$prompts_dir/${basename}.prompt.md"

    # Create prompt file with agent frontmatter
    cat > "$prompt_file" <<EOF
---
agent: ${basename}
---
EOF
  done
}

build_variant() {

  local agent=$1 script=$2

  local base_dir="$GENRELEASES_DIR/sdd-${agent}-package-${script}"

  echo "Building $agent ($script) package..."

  mkdir -p "$base_dir"

  # Copy base structure but filter scripts by variant

  SPEC_DIR="$base_dir/.specify"

  mkdir -p "$SPEC_DIR"

  [[ -d memory ]] && { cp -r memory "$SPEC_DIR/"; echo "Copied memory -> .specify"; }

  [[ -d templates/harness ]] && { cp -r templates/harness "$SPEC_DIR/"; echo "Copied templates/harness -> .specify/harness"; }

  # Copy scripts directory
  if [[ -d scripts ]]; then
    mkdir -p "$SPEC_DIR/scripts"
    cp -r scripts/* "$SPEC_DIR/scripts/"
    echo "Copied scripts/* -> .specify/scripts"
  fi

  [[ -d templates ]] && { mkdir -p "$SPEC_DIR/templates"; find templates -type f -not -path "templates/commands/*" -not -path "templates/harness/*" -not -path "templates/cursor-agents/*" -not -name "vscode-settings.json" -exec cp --parents {} "$SPEC_DIR"/ \; 2>/dev/null || true; echo "Copied templates -> .specify/templates"; }

  # Replace __AGENT_*__ placeholders in static template files (non-command templates)
  local skills_dir rules_file rules_dir config_dir
  skills_dir=$(agent_skills_dir "$agent")
  rules_file=$(agent_rules_file "$agent")
  rules_dir=$(agent_rules_dir "$agent")
  config_dir=$(agent_config_dir "$agent")

  if [[ -d templates/skills ]]; then
    mkdir -p "$base_dir/$skills_dir"
    cp -r templates/skills/* "$base_dir/$skills_dir/"
    echo "Copied templates/skills -> $skills_dir"

    # Replace __AGENT_*__ placeholders in copied skills
    find "$base_dir/$skills_dir" -type f -name "*.md" 2>/dev/null | while read -r skill_file; do
      sed -i \
        -e "s|__AGENT__|$agent|g" \
        -e "s|__AGENT_SKILLS_DIR__|$skills_dir|g" \
        -e "s|__AGENT_RULES_FILE__|$rules_file|g" \
        -e "s|__AGENT_CONFIG_DIR__|$config_dir|g" \
        "$skill_file"
    done
  fi

  if [[ -d templates/rules ]]; then
    mkdir -p "$base_dir/$rules_dir"
    cp -r templates/rules/* "$base_dir/$rules_dir/"
    echo "Copied templates/rules -> $rules_dir"

    # Replace __AGENT_*__ placeholders in copied rules
    find "$base_dir/$rules_dir" -type f -name "*.md" 2>/dev/null | while read -r rule_file; do
      sed -i \
        -e "s|__AGENT__|$agent|g" \
        -e "s|__AGENT_SKILLS_DIR__|$skills_dir|g" \
        -e "s|__AGENT_RULES_FILE__|$rules_file|g" \
        -e "s|__AGENT_CONFIG_DIR__|$config_dir|g" \
        "$rule_file"
    done
  fi

  find "$SPEC_DIR/templates" -type f -name "*.md" 2>/dev/null | while read -r tpl_file; do
    sed -i \
      -e "s|__AGENT__|$agent|g" \
      -e "s|__AGENT_SKILLS_DIR__|$skills_dir|g" \
      -e "s|__AGENT_RULES_FILE__|$rules_file|g" \
      -e "s|__AGENT_CONFIG_DIR__|$config_dir|g" \
      "$tpl_file"
  done

  # Replace __AGENT_*__ placeholders in scripts
  find "$SPEC_DIR/scripts" -type f \( -name "*.sh" -o -name "*.ps1" \) 2>/dev/null | while read -r script_file; do
    sed -i \
      -e "s|__AGENT__|$agent|g" \
      -e "s|__AGENT_SKILLS_DIR__|$skills_dir|g" \
      -e "s|__AGENT_RULES_FILE__|$rules_file|g" \
      -e "s|__AGENT_CONFIG_DIR__|$config_dir|g" \
      -e "s|__AGENT_TEMPLATES_DIR__|.specify/templates|g" \
      "$script_file"
  done

  # Inject variant into plan-template.md within .specify/templates if present

  local plan_tpl="$base_dir/.specify/templates/plan-template.md"

  if [[ -f "$plan_tpl" ]]; then

    plan_norm=$(tr -d '\r' < "$plan_tpl")

    # Extract script command from YAML frontmatter

    script_command=$(printf '%s\n' "$plan_norm" | awk -v sv="$script" '/^[[:space:]]*'"$script"':[[:space:]]*/ {sub(/^[[:space:]]*'"$script"':[[:space:]]*/, ""); print; exit}')

    if [[ -n $script_command ]]; then

      # Always prefix with .specify/ for plan usage

      script_command=".specify/$script_command"

      tmp_file=$(mktemp)

      # Replace {SCRIPT} placeholder with the script command and __AGENT__ with agent name

      substituted=$(sed "s|{SCRIPT}|${script_command}|g" "$plan_tpl" | tr -d '\r' | sed "s|__AGENT__|${agent}|g")

      # Strip YAML frontmatter from plan template output (keep body only)

      stripped=$(printf '%s\n' "$substituted" | awk 'BEGIN{fm=0;dash=0} /^---$/ {dash++; if(dash==1){fm=1; next} else if(dash==2){fm=0; next}} {if(!fm) print}')

      printf '%s\n' "$stripped" > "$plan_tpl"

    else

      echo "Warning: no plan-template script command found for $script in YAML frontmatter" >&2

    fi

  fi

  case $agent in

    claude)

      mkdir -p "$base_dir/.claude/commands"

      generate_commands claude md "\$ARGUMENTS" "$base_dir/.claude/commands" "$script"

      # Copy ECC components for Claude
      if [[ -d ecc-components/agents ]]; then
        mkdir -p "$base_dir/.claude/agents"
        cp ecc-components/agents/*.md "$base_dir/.claude/agents/"
        echo "Copied ECC agents -> .claude/agents"
      fi

      if [[ -d ecc-components/commands ]]; then
        cp ecc-components/commands/*.md "$base_dir/.claude/commands/"
        echo "Copied ECC commands -> .claude/commands"
      fi

      if [[ -d ecc-components/skills ]]; then
        mkdir -p "$base_dir/.claude/skills"
        cp -r ecc-components/skills/* "$base_dir/.claude/skills/"
        echo "Copied ECC skills -> .claude/skills"
      fi

      if [[ -d ecc-components/rules ]]; then
        mkdir -p "$base_dir/.claude/rules"
        cp -r ecc-components/rules/* "$base_dir/.claude/rules/"
        echo "Copied ECC rules -> .claude/rules"
      fi

      if [[ -f ecc-components/hooks/hooks.json ]]; then
        cp ecc-components/hooks/hooks.json "$base_dir/.claude/hooks-example.json"
        echo "Copied ECC hooks example -> .claude/hooks-example.json"
      fi
      ;;

    gemini)

      mkdir -p "$base_dir/.gemini/commands"

      generate_commands gemini toml "{{args}}" "$base_dir/.gemini/commands" "$script"

      [[ -f agent_templates/gemini/GEMINI.md ]] && cp agent_templates/gemini/GEMINI.md "$base_dir/GEMINI.md" ;;

    copilot)

      mkdir -p "$base_dir/.github/agents"

      generate_commands copilot agent.md "\$ARGUMENTS" "$base_dir/.github/agents" "$script"

      # Generate companion prompt files
      generate_copilot_prompts "$base_dir/.github/agents" "$base_dir/.github/prompts"

      # Create VS Code workspace settings
      mkdir -p "$base_dir/.vscode"

      [[ -f templates/vscode-settings.json ]] && cp templates/vscode-settings.json "$base_dir/.vscode/settings.json" ;;

    cursor-agent)

      mkdir -p "$base_dir/.cursor/commands"
      mkdir -p "$base_dir/.cursor/agents"

      generate_commands cursor-agent md "\$ARGUMENTS" "$base_dir/.cursor/commands" "$script"

      # Copy Cursor Subagent definitions for SDD phase delegation
      if [[ -d templates/cursor-agents ]]; then
        cp templates/cursor-agents/*.md "$base_dir/.cursor/agents/"
        echo "Copied Cursor Subagents -> .cursor/agents"
      fi ;;

    qwen)

      mkdir -p "$base_dir/.qwen/commands"

      generate_commands qwen toml "{{args}}" "$base_dir/.qwen/commands" "$script"

      [[ -f agent_templates/qwen/QWEN.md ]] && cp agent_templates/qwen/QWEN.md "$base_dir/QWEN.md" ;;

    opencode)

      mkdir -p "$base_dir/.opencode/command"

      generate_commands opencode md "\$ARGUMENTS" "$base_dir/.opencode/command" "$script" ;;

    windsurf)

      mkdir -p "$base_dir/.windsurf/workflows"

      generate_commands windsurf md "\$ARGUMENTS" "$base_dir/.windsurf/workflows" "$script"

      # Copy ECC components for Windsurf
      # if [[ -d ecc-components/commands ]]; then
      #   cp ecc-components/commands/*.md "$base_dir/.windsurf/workflows/"
      #   echo "Copied ECC commands -> .windsurf/workflows"
      # fi

      # if [[ -d ecc-components/skills ]]; then
      #   mkdir -p "$base_dir/.windsurf/skills"
      #   cp -r ecc-components/skills/* "$base_dir/.windsurf/skills/"
      #   echo "Copied ECC skills -> .windsurf/skills"
      # fi

      # if [[ -d ecc-components/rules ]]; then
      #   mkdir -p "$base_dir/.windsurf/rules"
      #   cp -r ecc-components/rules/* "$base_dir/.windsurf/rules/"
      #   echo "Copied ECC rules -> .windsurf/rules"
      # fi
      ;;

    codex)

      mkdir -p "$base_dir/.codex/prompts"

      generate_commands codex md "\$ARGUMENTS" "$base_dir/.codex/prompts" "$script"

      # Copy ECC components for Codex
      if [[ -d ecc-components/commands ]]; then
        cp ecc-components/commands/*.md "$base_dir/.codex/prompts/"
        echo "Copied ECC commands -> .codex/prompts"
      fi

      if [[ -d ecc-components/skills ]]; then
        mkdir -p "$base_dir/.codex/skills"
        cp -r ecc-components/skills/* "$base_dir/.codex/skills/"
        echo "Copied ECC skills -> .codex/skills"
      fi

      if [[ -d ecc-components/rules ]]; then
        mkdir -p "$base_dir/.codex/rules"
        cp -r ecc-components/rules/* "$base_dir/.codex/rules/"
        echo "Copied ECC rules -> .codex/rules"
      fi
      ;;

    kilocode)

      mkdir -p "$base_dir/.kilocode/workflows"

      generate_commands kilocode md "\$ARGUMENTS" "$base_dir/.kilocode/workflows" "$script" ;;

    auggie)

      mkdir -p "$base_dir/.augment/commands"

      generate_commands auggie md "\$ARGUMENTS" "$base_dir/.augment/commands" "$script" ;;

    roo)

      mkdir -p "$base_dir/.roo/commands"

      generate_commands roo md "\$ARGUMENTS" "$base_dir/.roo/commands" "$script" ;;

    q)

      mkdir -p "$base_dir/.amazonq/prompts"

      generate_commands q md "\$ARGUMENTS" "$base_dir/.amazonq/prompts" "$script" ;;

    codebuddy)

      mkdir -p "$base_dir/.codebuddy/commands"

      generate_commands codebuddy md "\$ARGUMENTS" "$base_dir/.codebuddy/commands" "$script" ;;

    amp)

      mkdir -p "$base_dir/.agents/commands"

      generate_commands amp md "\$ARGUMENTS" "$base_dir/.agents/commands" "$script" ;;

    shai)

      mkdir -p "$base_dir/.shai/commands"

      generate_commands shai md "\$ARGUMENTS" "$base_dir/.shai/commands" "$script" ;;

    bob)

      mkdir -p "$base_dir/.bob/commands"

      generate_commands bob md "\$ARGUMENTS" "$base_dir/.bob/commands" "$script" ;;

  esac

  ( cd "$base_dir" && zip -r "../spec-kit-template-${agent}-${script}-${PACKAGE_VERSION}.zip" . )

  echo "Created $GENRELEASES_DIR/spec-kit-template-${agent}-${script}-${PACKAGE_VERSION}.zip"

}

# Determine agent list

ALL_AGENTS=(claude gemini copilot cursor-agent qwen opencode windsurf codex kilocode auggie roo codebuddy amp shai q bob)

ALL_SCRIPTS=(sh ps)

norm_list() {

  # convert comma+space separated -> line separated unique while preserving order of first occurrence

  tr ',\n' '  ' | awk '{for(i=1;i<=NF;i++){if(!seen[$i]++){printf((out?"\n":"") $i);out=1}}}END{printf("\n")}'

}

validate_subset() {

  local type=$1; shift; local allowed_name=$1; shift; local items=("$@")

  local invalid=0

  for it in "${items[@]}"; do

    local found=0

    eval "allowed=(\"\${${allowed_name}[@]}\")"

    for a in "${allowed[@]}"; do [[ $it == "$a" ]] && { found=1; break; }; done

    if [[ $found -eq 0 ]]; then

      echo "Error: unknown $type '$it' (allowed: ${allowed[*]})" >&2

      invalid=1

    fi

  done

  return $invalid

}

if [[ -n ${AGENTS:-} ]]; then

  AGENT_LIST=($(printf '%s' "$AGENTS" | norm_list))

  validate_subset agent ALL_AGENTS "${AGENT_LIST[@]}" || exit 1

else

  AGENT_LIST=("${ALL_AGENTS[@]}")

fi

if [[ -n ${SCRIPTS:-} ]]; then

  SCRIPT_LIST=($(printf '%s' "$SCRIPTS" | norm_list))

  validate_subset script ALL_SCRIPTS "${SCRIPT_LIST[@]}" || exit 1

else

  SCRIPT_LIST=("${ALL_SCRIPTS[@]}")

fi

echo "Agents: ${AGENT_LIST[*]}"

echo "Scripts: ${SCRIPT_LIST[*]}"

for agent in "${AGENT_LIST[@]}"; do

  for script in "${SCRIPT_LIST[@]}"; do

    build_variant "$agent" "$script"

  done

done

echo "Archives in $GENRELEASES_DIR:"

ls -1 "$GENRELEASES_DIR"/spec-kit-template-*-"${PACKAGE_VERSION}".zip

# Move all generated zip files to the root directory for GitHub Actions
echo "Moving archives to root directory..."
mv "$GENRELEASES_DIR"/spec-kit-template-*-"${PACKAGE_VERSION}".zip ./

echo "Archives moved to root directory:"
ls -1 spec-kit-template-*-"${PACKAGE_VERSION}".zip
