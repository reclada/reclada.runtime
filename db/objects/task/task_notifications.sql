DO LANGUAGE PLpgSQL $block$
BEGIN
    IF reclada_object.list('{"class": "Message", "attributes": {"class": "Task", "event": "create"}}') is null THEN
        PERFORM reclada_object.create('{"class": "Message", "attributes": {"channelName": "task_created", "class": "Task", "event": "create", "attrs": ["status", "type"]}}'::jsonb);
    END IF;
    IF reclada_object.list('{"class": "Message", "attributes": {"class": "Task", "event": "update"}}') is null THEN
        PERFORM reclada_object.create('{"class": "Message", "attributes": {"channelName": "task_updated", "class": "Task", "event": "update", "attrs": ["status", "type"]}}'::jsonb);
    END IF;
    IF reclada_object.list('{"class": "Message", "attributes": {"class": "Task", "event": "delete"}}') is null THEN
        PERFORM reclada_object.create('{"class": "Message", "attributes": {"channelName": "task_deleted", "class": "Task", "event": "delete", "attrs": ["type"]}}'::jsonb);
    END IF;
END;
$block$;