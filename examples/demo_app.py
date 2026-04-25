import streamlit as st
import os
import tempfile
import shutil
import json
from vtr_standard.poc.vtr_container import VTRContainer
from vtr_standard.poc.validator import VTRValidator

# --- CONFIG ---
st.set_page_config(
    page_title="VTR Truth Terminal",
    page_icon="🎥",
    layout="centered"
)

st.title("🎥 VTR Truth Terminal")
st.markdown("### The Hardware-Attested Media Validator")

# --- SIDEBAR: GENERATOR ---
st.sidebar.header("1. Signer (Mock Camera)")
st.sidebar.markdown("Simulate a camera sensor capturing and signing a video.")

# Use a specific mock sensor ID
sensor_id = st.sidebar.text_input(
    "Sensor ID (PRNU Source)", "SENSOR_ANDROID_PIXEL_99"
)
allow_ai = st.sidebar.checkbox("Allow AI Training?", value=False)

uploaded_file_sign = st.sidebar.file_uploader(
    "Upload Video to Sign", type=["mp4", "mov", "avi"]
)

if st.sidebar.button("🔒 Sign Video") and uploaded_file_sign:
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_vid_path = os.path.join(tmp_dir, "video.mp4")
        with open(tmp_vid_path, "wb") as f:
            shutil.copyfileobj(uploaded_file_sign, f)

        try:
            # Create Container
            container = VTRContainer(tmp_vid_path, sensor_id_mock=sensor_id)
            # We need to handle the sidecar path manually
            # since VTRContainer writes to disk next to file
            container.create_sidecar(
                allow_ai_training=allow_ai, overwrite=True
            )

            sidecar_path = f"{tmp_vid_path}.vtr.json"

            with open(sidecar_path, "r") as f:
                sidecar_json = json.load(f)

            st.sidebar.success("Signed Successfully!")
            st.sidebar.json(sidecar_json)

            # Allow user to download the sidecar
            st.sidebar.download_button(
                label="Download .vtr.json",
                data=json.dumps(sidecar_json, indent=4),
                file_name="video.vtr.json",
                mime="application/json"
            )

        except Exception as e:
            st.sidebar.error(f"Error signing: {e}")

# --- MAIN: VALIDATOR ---
st.header("2. Validator (The Truth Check)")
st.markdown("Verify the integrity of a video against its hardware signature.")

col1, col2 = st.columns(2)

with col1:
    vid_file = st.file_uploader(
        "Step A: Upload Video",
        type=["mp4", "mov", "avi"],
        key="v"
    )

with col2:
    sidecar_file = st.file_uploader(
        "Step B: Upload .vtr.json",
        type=["json"],
        key="s"
    )

if vid_file and sidecar_file:
    if st.button("🔍 Verify Integrity"):
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Save to temp for processing
            t_vid_path = os.path.join(tmp_dir, "video.mp4")
            with open(t_vid_path, "wb") as f:
                shutil.copyfileobj(vid_file, f)

            t_json_path = os.path.join(tmp_dir, "sidecar.json")
            with open(t_json_path, "wb") as f:
                shutil.copyfileobj(sidecar_file, f)

            validator = VTRValidator(config=config)
            result = validator.validate_container(t_vid_path, t_json_path)

            if result.is_valid:
                st.success("✅ **VERIFICATION SUCCESSFUL**")
                st.balloons()
                st.markdown("---")
                m_root = result.details.get("merkle_root", "")[:16]
                st.markdown(
                    f"**Authenticated Sensor:** `{m_root}...`"
                )  # proxy
                st.markdown("**Liveness Check:** `PASS`")
                st.json(result.details)
            else:
                st.error("❌ **VERIFICATION FAILED**")
                st.markdown(f"**Error Code:** `{result.error_code}`")
                st.markdown(f"**Reason:** {result.message}")
                with st.expander("Technical Details"):
                    st.json(result.details)

                # Fun tamper viz
                st.warning("⚠️ **Tamper Evidence Detected**")
                st.text(
                    "The Merkle Root of the video content "
                    "does not match the hardware signature."
                )
