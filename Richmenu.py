def createRichmenu():
    try:
        # define a new richmenu
        rich_menu_to_create = RichMenu(
            size=RichMenuSize(width=1200, height=405),
            selected=True,
            name='richmenu for randomchat',
            chat_bar_text='TAP HERE',
            areas=[
                RichMenuArea(
                    bounds=RichMenuBounds(x=0, y=0, width=480, height=405),
                    action=MessageAction(text=config.REMOVE)
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=480, y=0, width=720, height=405),
                    action=MessageAction(text=config.NEXT)
                )
            ]
        )
        richMenuId = line_bot_api.create_rich_menu(
            rich_menu=rich_menu_to_create)

        # upload an image for rich menu
        path = 'image path for richmenu'

        with open(path, 'rb') as f:
            line_bot_api.set_rich_menu_image(
                richMenuId, "static/img/zakoshi1.jpeg", f)

        # set the default rich menu
        line_bot_api.set_default_rich_menu(richMenuId)

        result = True

    except Exception:
        result = False

    return result
