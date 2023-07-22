#! /bin/sh

DATA_DIR="./data"
EXTRACTED_DIR="./extracted"
FIGURES_DIR="./figures"

mkdir -p "$EXTRACTED_DIR"
mkdir -p "$FIGURES_DIR"

for archive in $DATA_DIR/*.tar.gz
do
    bname=$(basename "$archive")

    dir_name="$EXTRACTED_DIR/${bname%.tar.gz}"
    mkdir -p "$dir_name"

    tar xf "$archive" --directory "$dir_name"
done

gen_figures() {
    name="$1"
    echo "Generating figures for $name..."
    ./matplotlib_scripts/$name.py
}

gen_figures separated_models
gen_figures rcsa
