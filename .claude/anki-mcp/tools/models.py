"""Note type (model) introspection."""
from core import mcp, _call


@mcp.tool()
def model_names() -> list[str]:
    """Return all note type (model) names in the collection."""
    return _call("modelNames")


@mcp.tool()
def model_field_names(model_name: str) -> list[str]:
    """Return the field names for a note type, in definition order."""
    return _call("modelFieldNames", modelName=model_name)


@mcp.tool()
def model_templates(model_name: str) -> dict:
    """Return card template definitions (Front/Back HTML) for a note type."""
    return _call("modelTemplates", modelName=model_name)


@mcp.tool()
def model_styling(model_name: str) -> dict:
    """Return CSS styling for a note type."""
    return _call("modelStyling", modelName=model_name)


@mcp.tool()
def rename_model_field(model_name: str, old_field_name: str, new_field_name: str) -> None:
    """Rename a field in an existing note type."""
    return _call("modelFieldRename", modelName=model_name, oldFieldName=old_field_name, newFieldName=new_field_name)


@mcp.tool()
def add_model_field(model_name: str, field_name: str, index: int | None = None) -> None:
    """Add a new field to an existing note type. index sets insertion position; omit to append."""
    params = {"modelName": model_name, "fieldName": field_name}
    if index is not None:
        params["index"] = index
    return _call("modelFieldAdd", **params)


@mcp.tool()
def remove_model_field(model_name: str, field_name: str) -> None:
    """Remove a field from an existing note type. All note data in that field is lost."""
    return _call("modelFieldRemove", modelName=model_name, fieldName=field_name)


@mcp.tool()
def change_note_type(
    note_ids: list[int],
    old_model: str,
    new_model: str,
    field_mapping: dict[str, str] | None = None,
    template_mapping: dict[str, str] | None = None,
) -> None:
    """Change the note type of notes. field_mapping and template_mapping are {old_name: new_name};
    omit both to auto-map by matching field/template names."""
    old_fields = _call("modelFieldNames", modelName=old_model)
    new_fields = _call("modelFieldNames", modelName=new_model)
    old_tmpls = list(_call("modelTemplates", modelName=old_model).keys())
    new_tmpls = list(_call("modelTemplates", modelName=new_model).keys())

    def name_to_idx_map(old_names, new_names, name_map):
        result = {}
        for i, old in enumerate(old_names):
            target = name_map.get(old, old) if name_map else old
            result[str(i)] = new_names.index(target) if target in new_names else None
        return result

    return _call(
        "changeNoteType",
        notes=note_ids,
        oldModel=old_model,
        newModel=new_model,
        fieldMapping=name_to_idx_map(old_fields, new_fields, field_mapping),
        templateMapping=name_to_idx_map(old_tmpls, new_tmpls, template_mapping),
    )


@mcp.tool()
def update_model_templates(model_name: str, templates: dict) -> None:
    """Update card template HTML for an existing note type.

    Before calling, read resource anki://template-reference via ReadMcpResourceTool.
    templates format: {"Card 1": {"Front": "<html>", "Back": "<html>"}, ...}
    """
    return _call("updateModelTemplates", model={"name": model_name, "templates": templates})


@mcp.tool()
def update_model_styling(model_name: str, css: str) -> None:
    """Replace the CSS stylesheet for an existing note type.

    Before calling, read resource anki://template-reference via ReadMcpResourceTool.
    """
    return _call("updateModelStyling", model={"name": model_name, "css": css})


@mcp.tool()
def create_model(model_name: str, fields: list[str], is_cloze: bool = False) -> dict:
    """Create a new note type. is_cloze=True sets cloze template and isCloze flag correctly."""
    if is_cloze:
        front_html = "{{cloze:" + fields[0] + "}}"
        back_parts = ["{{cloze:" + fields[0] + "}}"] + ["{{" + f + "}}" for f in fields[1:]]
        back_html = "<br>".join(back_parts)
    else:
        front_html = "{{" + fields[0] + "}}"
        back_parts = ["{{" + f + "}}" for f in fields[1:]]
        back_html = "{{FrontSide}}<hr id=answer>" + "<br>".join(back_parts)
    css = ".card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; }"
    return _call(
        "createModel",
        modelName=model_name,
        inOrderFields=fields,
        isCloze=is_cloze,
        cardTemplates=[{"Name": "Card 1", "Front": front_html, "Back": back_html}],
        css=css,
    )
