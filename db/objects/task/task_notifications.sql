DO LANGUAGE PLpgSQL $block$
BEGIN
    IF reclada_object.list('{"class": "Message", "attrs": {"class": "Task", "event": "create"}}') is null THEN
        PERFORM reclada_object.create('{"class": "Message", "attrs": {"channelName": "task_created", "class": "Task", "event": "create", "attrs": ["status", "type"]}}'::jsonb);
    END IF;
    IF reclada_object.list('{"class": "Message", "attrs": {"class": "Task", "event": "update"}}') is null THEN
        PERFORM reclada_object.create('{"class": "Message", "attrs": {"channelName": "task_updated", "class": "Task", "event": "update", "attrs": ["status", "type"]}}'::jsonb);
    END IF;
    IF reclada_object.list('{"class": "Message", "attrs": {"class": "Task", "event": "delete"}}') is null THEN
        PERFORM reclada_object.create('{"class": "Message", "attrs": {"channelName": "task_deleted", "class": "Task", "event": "delete", "attrs": ["type"]}}'::jsonb);
    END IF;
END;
$block$;