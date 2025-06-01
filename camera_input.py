import cv2
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

def configure_camera(master=None):
    """
    Opens a small tkinter dialog to configure camera parameters and start recording.
    Returns path to the saved video file or None if canceled.
    """
    result = {'path': None}

    def on_start():
        idx = int(cam_index_var.get())
        w = int(width_var.get())
        h = int(height_var.get())
        dur = float(duration_var.get()) if duration_var.get() else None
        out_path = f"camera_capture_{int(time.time())}.mp4"
        dlg.destroy()
        # run capture in thread to avoid blocking UI
        threading.Thread(target=_capture, args=(idx, (w, h), dur, out_path, result), daemon=True).start()

    def _capture(idx, res, duration, out_path, result_dict):
        cap = cv2.VideoCapture(idx)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, res[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, res[1])
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(out_path, fourcc, 20.0, res)
        start = time.time()
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
            cv2.imshow('Recording - press Q to stop', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if duration and (time.time() - start) >= duration:
                break
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        result_dict['path'] = out_path
        messagebox.showinfo('Camera', f'Recording saved to {out_path}')

    dlg = tk.Toplevel(master)
    dlg.title('Camera Configuration')
    ttk.Label(dlg, text='Camera Index:').grid(row=0, column=0, padx=5, pady=5, sticky='w')
    cam_index_var = tk.StringVar(value='0')
    ttk.Entry(dlg, textvariable=cam_index_var, width=4).grid(row=0, column=1, padx=5, pady=5)
    ttk.Label(dlg, text='Resolution WxH:').grid(row=1, column=0, padx=5, pady=5, sticky='w')
    width_var = tk.StringVar(value='640')
    height_var = tk.StringVar(value='480')
    ttk.Entry(dlg, textvariable=width_var, width=6).grid(row=1, column=1, padx=2, pady=5, sticky='w')
    ttk.Entry(dlg, textvariable=height_var, width=6).grid(row=1, column=2, padx=2, pady=5, sticky='w')
    ttk.Label(dlg, text='Duration (sec, optional):').grid(row=2, column=0, padx=5, pady=5, sticky='w')
    duration_var = tk.StringVar()
    ttk.Entry(dlg, textvariable=duration_var, width=6).grid(row=2, column=1, padx=5, pady=5)
    ttk.Button(dlg, text='Start Recording', command=on_start).grid(row=3, column=0, columnspan=3, pady=10)
    dlg.grab_set()
    dlg.wait_window()
    return result['path']
