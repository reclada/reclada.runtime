SELECT reclada_object.create_subclass('{
    "class": "RecladaObject",
    "attrs": {
        "newClass": "FileExtension",
        "properties": {
            "value": {"type": "string"},
            "mimeType": {"type": "string"}
        },
        "required": ["value", "mimeType"]
    }
}'::jsonb);