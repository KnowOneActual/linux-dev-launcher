#!/usr/bin/env bash
set -e

echo "Installing Linux Dev Launcher..."

INSTALL_DIR="$(pwd)"
TEMPLATE_FILE="open-dev-env.desktop.template"

if [[ ! -f "$TEMPLATE_FILE" ]]; then
    echo "Error: Must run install.sh from within the linux-dev-launcher directory."
    exit 1
fi

# 1. KDE / Dolphin Setup
KDE_DIRS=(
    "$HOME/.local/share/kio/servicemenus"
    "$HOME/.local/share/kservices5/ServiceMenus"
)

for dir in "${KDE_DIRS[@]}"; do
    mkdir -p "$dir"
    DESKTOP_FILE="$dir/open-dev-env.desktop"
    sed "s|{{INSTALL_DIR}}|$INSTALL_DIR|g" "$TEMPLATE_FILE" > "$DESKTOP_FILE"
    chmod +x "$DESKTOP_FILE"
    echo "✓ Installed KDE/Dolphin ServiceMenu in: $dir"
done

# 2. GNOME / Nautilus Setup
NAUTILUS_DIR="$HOME/.local/share/nautilus/scripts"
mkdir -p "$NAUTILUS_DIR"
NAUTILUS_SCRIPT="$NAUTILUS_DIR/Open Dev Environment"

cat << 'EOF' > "$NAUTILUS_SCRIPT"
#!/usr/bin/env bash
# Nautilus passes selected files as arguments or newlines
if [ -n "$NAUTILUS_SCRIPT_SELECTED_FILE_PATHS" ]; then
    TARGET=$(echo "$NAUTILUS_SCRIPT_SELECTED_FILE_PATHS" | head -n 1)
else
    TARGET="$PWD"
fi
python3 "{{INSTALL_DIR}}/open_dev_env.py" "$TARGET"
EOF

sed -i "s|{{INSTALL_DIR}}|$INSTALL_DIR|g" "$NAUTILUS_SCRIPT"
chmod +x "$NAUTILUS_SCRIPT"
echo "✓ Installed GNOME/Nautilus Script in: $NAUTILUS_DIR"

# 3. Cinnamon / Nemo Setup
NEMO_DIR="$HOME/.local/share/nemo/scripts"
mkdir -p "$NEMO_DIR"
NEMO_SCRIPT="$NEMO_DIR/Open Dev Environment"

cp "$NAUTILUS_SCRIPT" "$NEMO_SCRIPT"
chmod +x "$NEMO_SCRIPT"
echo "✓ Installed Cinnamon/Nemo Script in: $NEMO_DIR"

echo ""
echo "Installation complete!"
echo "You can now right-click a folder in your file manager to 'Open Dev Environment'."
