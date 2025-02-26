# List of file paths
file_paths = [
    "./countfiles//inv1.csv", "./countfiles//inv2.csv", "./countfiles//met1.csv", "./countfiles//met10.csv",
    "./countfiles//met11.csv", "./countfiles//met12.csv", "./countfiles//met13.csv", "./countfiles//met14.csv",
    "./countfiles//met15.csv", "./countfiles//met2.csv", "./countfiles//met3.csv", "./countfiles//met4.csv",
    "./countfiles//met5.csv", "./countfiles//met6.csv", "./countfiles//met7.csv", "./countfiles//met8.csv",
    "./countfiles//met9.csv", "./countfiles//PbSTM18.csv", "./countfiles//PbSTM19.csv", "./countfiles//PbSTM21.csv",
    "./countfiles//PbSTM22.csv", "./countfiles//PbSTM23.csv", "./countfiles//PbSTM24.csv", "./countfiles//PbSTM25.csv",
    "./countfiles//PbSTM26.csv", "./countfiles//PbSTM27.csv", "./countfiles//PbSTM28.csv", "./countfiles//PbSTM29.csv",
    "./countfiles//PbSTM30.csv", "./countfiles//PbSTM31.csv", "./countfiles//PbSTM32.csv", "./countfiles//PbSTM33.csv",
    "./countfiles//PbSTM34.csv", "./countfiles//PbSTM35.csv", "./countfiles//PbSTM36.csv", "./countfiles//PbSTM37__C57BL6.csv",
    "./countfiles//PbSTM37_Balbc.csv", "./countfiles//PbSTM37_Rag1.csv", "./countfiles//PbSTM37_SCID.csv", "./countfiles//PbSTM37a.csv",
    "./countfiles//PbSTM38.csv", "./countfiles//PbSTM39.csv", "./countfiles//PbSTM40.csv", "./countfiles//PbSTM43.csv",
    "./countfiles//PbSTM44.csv", "./countfiles//PbSTM45.csv", "./countfiles//PbSTM46.csv", "./countfiles//PbSTM47b.csv",
    "./countfiles//PbSTM49.csv", "./countfiles//PbSTM50.csv", "./countfiles//PbSTM51.csv", "./countfiles//PbSTM52.csv",
    "./countfiles//PbSTM53.csv", "./countfiles//PbSTM54.csv", "./countfiles//PbSTM56.csv", "./countfiles//PbSTM57.csv",
    "./countfiles//PbSTM58.csv", "./countfiles//PbSTM59.csv", "./countfiles//PbSTM60.csv", "./countfiles//PbSTM61.csv",
    "./countfiles//PbSTM62.csv", "./countfiles//PbSTM63.csv", "./countfiles//PbSTM63b.csv", "./countfiles//PbSTM64.csv",
    "./countfiles//PbSTM65a.csv", "./countfiles//PbSTM66.csv", "./countfiles//PbSTM67B.csv", "./countfiles//PbSTM67C.csv",
    "./countfiles//PbSTM68.csv", "./countfiles//PbSTM85.csv", "./countfiles//PbSTM86.csv", "./countfiles//PbSTM87.csv",
    "./countfiles//PbSTM88.csv", "./countfiles//PbSTM89.csv", "./countfiles//PbSTM90.csv", "./countfiles//PbSTM91.csv",
    "./countfiles//stm26.csv", "./countfiles//stm27.csv", "./countfiles//stm28_2r.csv", "./countfiles//stm37_4r.csv"
]

# Write the file paths to a text file
output_path = "file_paths.txt"
with open(output_path, "w") as file:
    for path in file_paths:
        file.write(path + "\n")

output_path
