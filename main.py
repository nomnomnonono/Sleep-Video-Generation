import gradio as gr
from sleep_video_generator.generate import (
    archive_files,
    generate_image,
    generate_thumbnail,
    generate_video,
)


def main() -> None:
    with gr.Blocks() as demo:
        gr.Markdown("Sleep Video Generator")
        with gr.Row():
            with gr.Column(scale=1):
                image_generate_prompt = gr.Textbox(
                    "Test Prompt", label="Image Generate Prompt"
                )
                image_generate_button = gr.Button("Image Generate")

                thumbnail_text = gr.Textbox(
                    "Test Thumbnail Text", label="Thumbnail Text"
                )
                with gr.Accordion("Thumbnail Settings", open=False):
                    fontstyle = gr.Dropdown(
                        [
                            "FONT_HERSHEY_SIMPLEX",
                            "FONT_HERSHEY_PLAIN",
                            "FONT_HERSHEY_DUPLEX",
                            "FONT_HERSHEY_COMPLEX",
                            "FONT_HERSHEY_TRIPLEX",
                            "FONT_HERSHEY_COMPLEX_SMALL",
                            "FONT_HERSHEY_SCRIPT_SIMPLEX",
                            "FONT_HERSHEY_SCRIPT_COMPLEX",
                            "FONT_ITALIC",
                        ],
                        value="FONT_HERSHEY_SIMPLEX",
                        label="Font Style",
                    )
                    fontsize = gr.Slider(1, 10, 1, step=0.1, label="Font Size")
                    fontcolor = gr.ColorPicker(value="#ffffff", label="Font Color")
                    thickness = gr.Slider(1, 10, 1, step=1, label="Thickness")
                    linetype = gr.Dropdown(
                        ["LINE_AA", "LINE_4", "LINE_8", "FILLED"],
                        value="LINE_AA",
                        label="Line Type",
                    )
                thumbnail_generate_button = gr.Button("Thumbnail Generate")

                upload_audio = gr.File(label="Upload Audio")
                with gr.Accordion("Video Settings", open=False):
                    video_duration = gr.Slider(
                        3, 30, 10, step=1, label="Video Duration (minutes)"
                    )
                video_generate_button = gr.Button("Video Generate")

                folder_name = gr.Textbox("Folder Name", label="Folder Name")
                archive_button = gr.Button("Archive Files")
            with gr.Column(scale=1.5):
                image_output = gr.Image(label="Output image")
                thumbnail_path = gr.File(label="Output Thumbnail")
                video_output = gr.File(label="Output video")

        image_generate_button.click(
            generate_image,
            inputs=[
                image_generate_prompt,
            ],
            outputs=image_output,
        )

        thumbnail_generate_button.click(
            generate_thumbnail,
            inputs=[
                thumbnail_text,
                fontstyle,
                fontsize,
                fontcolor,
                thickness,
                linetype,
            ],
            outputs=[image_output, thumbnail_path],
        )

        video_generate_button.click(
            generate_video,
            inputs=[
                upload_audio,
                video_duration,
            ],
            outputs=video_output,
        )

        archive_button.click(
            archive_files,
            inputs=[folder_name],
        )

    demo.launch()


if __name__ == "__main__":
    main()
