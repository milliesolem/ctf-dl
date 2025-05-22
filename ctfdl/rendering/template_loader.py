import os


def list_available_templates():
    """
    Print available templates (folder structure and challenge output).
    """
    base_template_dir = os.path.join(os.path.dirname(__file__), "templates")
    folder_template_dir = os.path.join(base_template_dir, "folder_structure")

    print("\nAvailable Folder Structure Templates:")
    if os.path.isdir(folder_template_dir):
        for fname in os.listdir(folder_template_dir):
            if fname.endswith(".jinja"):
                logical_name = fname[:-6]
                print(f"- {logical_name}")

    print("\nAvailable Challenge Templates:")
    if os.path.isdir(base_template_dir):
        for fname in os.listdir(base_template_dir):
            if fname.endswith(".jinja"):
                logical_name = fname[:-6]
                print(f"- {logical_name}")

    print()
