

import React, { useState, useRef } from 'react';
import './inputs.css';

const InputRow = ({ onSubmit, onRecorded }) => {
    const [text, setText] = useState('');
    const [isRecording, setIsRecording] = useState(false);
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    const handleTextChange = (e) => {
        setText(e.target.value);
    };

    const handleSubmit = () => {
        if (text.trim() !== '') {
            onSubmit(text.trim());
            setText('');
        }
    };

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];

            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    audioChunksRef.current.push(e.data);
                }
            };

            mediaRecorder.onstop = () => {
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
            setIsRecording(true);
        } catch (err) {
            console.error('Recording failed:', err);
        }
    };

    const finishRecording = () => {
        const mediaRecorder = mediaRecorderRef.current;
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });

                /* const audioUrl = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioUrl);
                audio.play(); */

                onRecorded(audioBlob);
                setIsRecording(false);
            };
        }
    };

    const cancelRecording = () => {
        const mediaRecorder = mediaRecorderRef.current;
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            mediaRecorder.onstop = () => {
                setIsRecording(false);
            };
        }
    };

    return (
        <div className="input-container">
            <input
                type="text"
                className="text-input"
                value={text}
                onChange={handleTextChange}
                onKeyDown={(e) => {
                    if (e.key === 'Enter') {

                        handleSubmit()
                    }
                }}
            />
            <button className="submit-button" onClick={handleSubmit}>
                Submit
            </button>
            {!isRecording ? (
                <button className="record-button" onClick={startRecording}>
                    Record
                </button>
            ) : (
                <>
                    <button className="submit-button" onClick={finishRecording}>
                        Finish
                    </button>
                    <button className="record-button" onClick={cancelRecording}>
                        Cancel
                    </button>
                </>
            )}
        </div>
    );
};

export default InputRow;