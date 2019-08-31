import sys
import os

VOICE = False
LOG = ''
p_instruction = None
p_file = None


def main():
    # Chequeo de argumentos
    if len(sys.argv) == 1:
        sys.exit("No arguments. Usage: python script.py (path_to_instruction_file.ini)")

    # Chequea que la direccion entregada exista
    instruction_file = str(sys.argv[1])
    if not os.path.exists(instruction_file):
        sys.exit("File not found: " + instruction_file)

    # Transforma el archivo de instrucciones en una lista de parametros [path,offset,data_bytes]
    instructions = get_instructions(instruction_file)

    # Loopea y realiza cada instruccion
    for i in instructions:
        write_instruction(i)

    # Cierra el archivo que quedo abierto
    p_file.close()


def get_instructions(i_file):
    if VOICE: print("Getting instructions from " + str(i_file))

    # Abre el archivo de instruccion en modo de solo lectura
    with open(i_file, "r") as instructions:
        # Contador de lineas, usado para escribir errores al LOG
        line_num = 0

        # Lista que contiene todas las instrucciones formateadas
        i_list = []

        # Loopea por cada instruccion del archivo
        for instruction in instructions:
            # Updatea valor de linea
            line_num += 1

            # Salta las lineas vacías (Pero las mantiene en el contador de lineas para consistencia con el archivo)
            if instruction == '\n':
                continue

            # Borra el final de linea '\n'
            instruction = instruction[0:len(instruction) - 1]
            # Separa los parametros en duplas 'nombre=valor'
            params = instruction.split(",")

            # Inicializa valores, se sobreescribiran si la info entregada en la instruccion esta en el formato correcto
            path = offset = data_bytes = None

            # Loopea en cada parametro
            for param in params:
                # Separa el 'nombre' de el 'valor'
                param = param.split("=")
                param_name = param[0]
                param_value = param[1]

                # Si el parametro es la direccion, chequea que exista
                if param_name == 'file_name':
                    path = param_value
                    if path[0] == '\"' and path[len(path) - 1] == '\"':
                        path = path[1:len(path) - 1]
                    if not os.path.exists(path):
                        add_log("In line: " + str(line_num) + "\t File not found at: " + str(path))
                        path = None
                # Si el parametro es el offset, chequea que es un int
                elif param_name == 'offset':
                    try:
                        offset = int(param_value)
                    except ValueError:
                        offset = param_value
                        add_log("In line: " + str(line_num) + "\t The offset given is not an int(" + str(offset) + ")")
                        offset = None
                # Si el parametro es la informacion, interpretar en un array de bytes
                elif param_name == 'data':
                    try:
                        data = param_value
                        f_data = []

                        for i in range(0, len(data), 2):
                            f_data.append(data[i:i + 2])

                        data_bytes = bytearray([int(x, 16) for x in f_data])
                    except ValueError:
                        add_log("In line: " + str(line_num) + "\t Data not in the correct format [00~FF separated by ',']")

            # Si cualquiera de los parametros no esta en formato correcto, no agregar a lista de instrucciones
            to_append = True
            for item in [path, offset, data_bytes]:
                if item is None:
                    to_append = False
                    if VOICE: print("Invalid instruction in line " + str(line_num) + ", retrieved values " + str([path, offset, data_bytes]))
            if to_append:
                i_list.append([path, offset, data_bytes])

        if VOICE: print(str(len(i_list)) + " instructions found in " + str(line_num) + " lines")
        return i_list


def write_instruction(i):
    global p_instruction
    global p_file

    file = i[0]
    file_size = os.path.getsize(file)
    offset = i[1]
    data_bytes = i[2]
    data_length = len(data_bytes)

    if offset < 0 or offset > file_size:
        add_log("Instruction: " + i + "given offset(" + str(offset) + ") out of bounds [0," + str(os.path.getsize(file) - 1) + "]")
    if offset + data_length > file_size:
        add_log("Instruction: " + i + "data block(" + str(data_length) + " bytes) surpasses the original file limit by " +
                str(int(offset + data_length - file_size)) + " bytes")

    # If this is the first file in the batch, open, change it and leave it open
    if p_file is None:
        if VOICE: print("Case 1:First file\tWriting to " + str(file) + "\tOffset:" + str(offset) + "\tData:" + str(data_bytes))
        binary_file = open(file, "rb+")
        p_file = binary_file
        binary_file.seek(offset, 0)
        binary_file.write(data_bytes)
    # If working on the same file as the previous instruction, change it and leave it open
    elif p_instruction[0] == file:
        if VOICE: print("Case 2:Same  file \tWriting to " + str(file) + "\tOffset:" + str(offset) + "\tData:" + str(data_bytes))
        p_file.seek(offset)
        p_file.write(data_bytes)
    # If working on a different file, close the previous file, open the new one, change it and leave it open
    else:
        if VOICE: print("Case 3:New   file\tWriting to " + str(file) + "\tOffset:" + str(offset) + "\tData:" + str(data_bytes))
        p_file.close()
        binary_file = open(file, "rb+")
        p_file = binary_file
        binary_file.seek(offset, 0)
        binary_file.write(data_bytes)

    # Updatea la instruccion previa, para chequear en el siguiente ciclo
    if p_instruction is None:
        p_instruction = i
    else:
        p_instruction = i


def get_log():
    global LOG
    return LOG


def add_log(message):
    global LOG
    LOG += message + '\n'


def voice_log():
    global LOG
    if LOG != '':
        LOG = "ERROR LOG\n" + LOG
        print(LOG)
        input()
        sys.exit(1)
    else:
        print("Process finished without errors")
        sys.exit(0)


if __name__ == '__main__':
    main()
    voice_log()
