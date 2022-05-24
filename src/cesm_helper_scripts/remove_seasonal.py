import os
import sys

import matplotlib.pyplot as plt
import numpy as np


def remove_seasonal() -> None:
    # Check file path
    data = sys.stdin.readlines()
    filename = data[0].strip("\n")
    if not isinstance(filename, str) or filename[-4:] != ".npz":
        raise TypeError(f"Are you sure {filename} is a valid .npz file?")
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Cannot find file named {filename}.")
    base = filename[:-4]
    with np.load(filename, "r") as f:
        times = f["times"]
        values = f["data"]
    # Remove seasonal cycle in frequency domain
    # print(times)
    fr = np.fft.fftfreq(len(times), times[1] - times[0])
    sg = np.fft.fft(values)
    plt.figure()
    plt.semilogy(fr, sg.real, label="real")
    plt.semilogy(fr, sg.imag, label="imag")
    plt.legend()
    idx = np.argwhere((fr > 0.7) & (fr < 10.3))
    sg[idx] = sg[idx].imag
    idx = np.argwhere((fr > -10.3) & (fr < -0.7))
    sg[idx] = sg[idx].imag
    sg_time = np.fft.ifft(sg)
    sg_real = sg_time.real.astype(np.float32)

    plt.figure()
    plt.plot(times, values, label="original")
    plt.plot(times, sg_real, label="removed")
    plt.legend()
    plt.figure()
    plt.semilogy(fr, sg.real, label="real")
    plt.semilogy(fr, sg.imag, label="imag")
    plt.legend()
    plt.show()

    np.savez(f"{base}_seasonal_removed.npz", times=times, data=sg_real)


if __name__ == "__main__":
    remove_seasonal()
