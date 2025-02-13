import bpy

class DCC_PT_Panel(bpy.types.Panel):
    bl_label = "DCC Plugin UI"
    bl_idname = "DCC_PT_PANEL"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "DCC Plugin"

    def draw(self, context):
        layout = self.layout

        # Object Selection
        row = layout.row()
        row.label(text="Active Object:")
        row = layout.row()
        row.prop(context.active_object, "name", text="")

        # Transform Controls
        layout.label(text="Transform Controls:")
        col = layout.column()
        col.prop(context.active_object, "location", text="Location")
        col.prop(context.active_object, "rotation_euler", text="Rotation")
        col.prop(context.active_object, "scale", text="Scale")

        # Server Endpoint Dropdown
        layout.label(text="Server Endpoint:")
        layout.prop(context.scene, "dcc_server_endpoint", text="")

        # Submit Button
        layout.operator("dcc.submit_operator", text="Submit to Server")
