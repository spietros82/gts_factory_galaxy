# Runtime / licence record

No new downloads (0 bytes of the 5GB allowance). Existing project .venv: Python3.12.3, NumPy2.3.5, Pillow11.3.0, scikit-learn1.8.0, SciPy1.18.1, joblib1.6.0. Trained forest runs in sklearn CPU code with n_jobs2; no GPU/NPU kernels requested. Actual live CPU execution evidenced by runtime model path and CPU-only implementation, not device availability. Scene rendering remains Radeon/OpenGLCore.

Unity6000.6.5f1 Linux Mono release, Built-in pipeline. Existing installed qwen3:8b Q4_K_M via Ollama0.40.1 for explanation only. Gemma not rerun. No model weights bundled.

Scikit-learn BSD-3-Clause: https://github.com/scikit-learn/scikit-learn/blob/1.8.0/COPYING ; runtime classifier API: https://scikit-learn.org/1.8/modules/generated/sklearn.ensemble.RandomForestClassifier.html . Scores are not automatically calibrated: https://scikit-learn.org/stable/modules/calibration.html . NumPy/SciPy BSD-style, Pillow HPND, joblib BSD-3-Clause; exact installed metadata/licences retained in environment record. Existing procedural asset ownership/Unity licensing applies. New model weights generated locally, not derived from third-party pretrained weights; external redistribution not presumed authorised.
