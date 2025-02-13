bl_info = {
    "name": "DCC Plugin for Transform Operations",
    "blender": (4, 0, 0),
    "category": "Object"
}

import bpy
from .panel import DCC_PT_Panel
from .submit_operator import DCC_OT_SubmitOperator

def register():
    bpy.utils.register_class(DCC_PT_Panel)
    bpy.utils.register_class(DCC_OT_SubmitOperator)
    bpy.types.Scene.dcc_server_endpoint = bpy.props.StringProperty(
        name="Server Endpoint",
        default="http://localhost:5000/transform"
    )

def unregister():
    bpy.utils.unregister_class(DCC_PT_Panel)
    bpy.utils.unregister_class(DCC_OT_SubmitOperator)
    del bpy.types.Scene.dcc_server_endpoint

if __name__ == "__main__":
    register()
