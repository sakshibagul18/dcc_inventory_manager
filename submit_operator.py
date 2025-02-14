import bpy
import requests

class DCC_OT_SubmitOperator(bpy.types.Operator):
    bl_idname = "dcc.submit_operator"
    bl_label = "Submit to Server"

    def execute(self, context):
        # Get the selected server endpoint
        url = context.scene.dcc_server_endpoint

        # Get the active object
        obj = context.active_object
        if obj is None:
            self.report({'WARNING'}, "No active object selected!")
            print("WARNING: No active object selected!")
            return {'CANCELLED'}

        # Prepare transform data
        data = {
            "location": list(obj.location),
            "rotation": list(obj.rotation_euler),
            "scale": list(obj.scale)
        }

        # Print to Blender's Terminal (System Console)
        log_message = f"Sending transform data: {data}"
        print(log_message)  # ✅ Log to Blender's console

        try:
            # Send POST request to the server
            response = requests.post(url, json=data)
            print(f"Server Response: {response.status_code}, {response.text}")  # ✅ Log response

            if response.status_code == 200:
                self.report({'INFO'}, "Data sent successfully!")
            else:
                self.report({'ERROR'}, f"Error: {response.status_code}")
        except Exception as e:
            self.report({'ERROR'}, f"Connection failed: {e}")
            print(f"ERROR: Connection failed: {e}")  # ✅ Log exception in terminal

        return {'FINISHED'}

