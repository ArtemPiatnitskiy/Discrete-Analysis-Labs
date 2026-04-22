```cpp
        uint8_t get_bit(std::string& key, size_t index) {
            if (index == 0) return 0;

            size_t byte_index = (index - 1) / 8;

            if(byte_index >= key.length()) return 0;

            uint8_t mask = 1;

            uint8_t byte = key[(index - 1) / 8];
            // Считаем, что мы идём по байту слева направо, тогда наши индексы будут располагаться так:
            // 11111111 -> 01234567, где 0 - самый старший бит, а 7 - самый младший
            mask = (1 << (7 - (index - 1) % 8));

            return ((byte & mask) == 0 ? 0 : 1);
        }
```

```cpp
size_t get_first_bit_diff(const std::string& key1, const std::string& key2) {
            size_t len_key1 = key1.length(), len_key2 = key2.length();
            size_t n = std::max(len_key1, len_key2);

            for (size_t i = 0; i < n; ++i) {
                uint8_t c1 = (i < len_key1) ? static_cast<uint8_t>(key1[i]) : 0;
                uint8_t c2 = (i < len_key2) ? static_cast<uint8_t>(key2[i]) : 0;

                if (c1 != c2) { 
                    uint8_t diff = c1 ^ c2;

                    size_t position = 7;
                    while (!(diff & (1 << position))) {
                        --position;
                    }
                    return i * 8 + (7 - position) + 1;
                }
            }
            return 0;
        }
```

Разберёмся, как мы находим первый различающийся бит

Мы идём от 7 к 0 и пытаемся найти самый левый бит, который отличается.

В цикле проверка такая `not(diff & (1 << possition))` , это означает, что мы начинаем сравнение с самого левого бита:
`1 << 7 -> 00000001 << 7 = 10000000` и уменьшаем позицию.

Как только у нас появилось различие, выходим из цикла и возвращаем значение `i * 8 + (7 - possition)` - Число полных байт и то, на какой позиции в бите различие, тогда получим реальный индекс на котором в ключе у нас различие.

# Логика вставки

Пока что написан вариант с вставкой в  пустой корень

Если дерево пустое, то вставляем в корень. Корень пустой, если был вызван дефолтный конструктор.

Если же был вызван конструктор с вставкой первого элемента, то тогда мы начинаем спуск.

```cpp
void insert(const std::string& key, const T& data) {
            if (root == nullptr) {
                root = new Node<T>(key, data, 0);
                root->set_left(root);   
                return;
            }

            Node<T>* prev = nullptr;
            Node<T>* current = root;

            prev = current;
            current = current->get_left();

            while(current->get_index() > prev->get_index()) {
                prev = current;
                uint8_t bit = get_bit(key, current->get_index());

                current = (bit == 0) ? current->get_left() : current->get_right();

            }
        }
```

Сейчас самое интересное

В спуске мы нашли индекс, когда у нас индексы не убывают, то есть ситуация, что индекс `a >= b` 

Дальше мы нашли первый бит слева, который различается в ключах текущего и ключа, который мы передали

И теперь мы должны снова спустить по дереву, начиная от корня, чтобы успешно вставить новый узел

```cpp
        void insert(const std::string& key, const T& data) {
            if (root == nullptr) {
                root = new Node<T>(key, data, 0);
                root->set_left(root);   
                return;
            }

            Node<T>* prev = root;
            Node<T>* current = root->get_left();

            while(current->get_index() > prev->get_index()) {
                prev = current;
                uint8_t bit = get_bit(key, current->get_index());

                current = (bit == 0) ? current->get_left() : current->get_right();
            }

            // if (key == current->get_key()) {};


            size_t diff_bit = get_first_bit_diff(key, current->get_key());


        }
```

```cpp
void insert(const std::string& key, const T& data) {
            if (root == nullptr) {
                root = new Node<T>(key, data, 0);
                root->set_left(root);   
                return;
            }

            Node<T>* prev = root;
            Node<T>* current = root->get_left();

            while(current->get_index() > prev->get_index()) {
                prev = current;
                uint8_t bit = get_bit(key, current->get_index());

                current = (bit == 0) ? current->get_left() : current->get_right();
            }

            // if (key == current->get_key()) {};


            size_t bit_diff_index = get_first_bit_diff(key, current->get_key());

            prev = root;
            current = root->get_left();


            while (current->get_index() > prev->get_index() && current->get_index() < bit_diff_index) {
                prev = current;

                uint8_t bit = get_bit(key, current->get_index());

                current = (bit == 0) ? current->get_left() : current->get_right();
            }

            Node<T>* newNode = new Node<T>(key, data, bit_diff_index);
            uint8_t bit = get_bit(key, bit_diff_index);

            newNode->set_left(bit == 0 ? newNode : current);
            newNode->set_right(bit == 0 ? current : newNode);

            if (prev == root) {
                prev->set_left(newNode);
            }
            else {
                uint8_t prevbit = get_bit(key, prev->get_index());
                if (prevbit == 1) prev->set_right(newNode);
                else prev->set_left(newNode);
            }




        }
```

Разбор на примере

Давай вставим два ключа: **"A"** и **"B"**.  
Для простоты возьмем их коды в ASCII:

- **'A'** = `01000001`
- **'B'** = `01000010`

Шаг 1: Вставка "A" (Дерево пустое)

1. `root == nullptr`, срабатывает первый `if`.
2. Создается узел: `Node("A", index: 0)`.
3. `root->left` указывает на самого себя.  
   **Дерево:** `Header(A) --left--> Header(A)`.

Шаг 2: Вставка "B"

1. `root` не null. Первый спуск: `prev = Header`, `current = Header->left` (тоже Header).
2. `current->index (0) > prev->index (0)` — Ложь. Цикл пропускается.
3. `bit_diff_index`:
   - 'A': `0 1 0 0 0 0 0 1`
   - 'B': `0 1 0 0 0 0 1 0`
   - Разница в 7-м и 8-м битах. `get_first_bit_diff` вернет **7**.
4. Второй спуск: ищем место для индекса 7.
   - Начинаем с `root`. `current(index 0) < bit_diff_index(7)`, но `current->index > prev->index` снова Ложь.
   - Остаемся на `prev = root`.
5. Создаем `newNode("B", index: 7)`.
6. Бит "B" на позиции 7 равен **1**.
   - `newNode->left = current` (это Header/A).
   - `newNode->right = newNode` (петля на себя).
7. Привязка к `prev` (root):
   - `root->set_left(newNode)`.

**Итог в памяти:**

- **Root (A, idx 0)**: лево ведет к **Node B**.
- **Node B (B, idx 7)**: лево ведет к **Root (A)** (там мы найдем ключ "A"), право ведет к **себе** (там мы найдем ключ "B").

Что мы получили?

Теперь, если мы ищем "A":

1. Идем в `root->left` -> попадаем в `Node B`.
2. В `Node B` смотрим 7-й бит "A". Он равен `0`.
3. Идем влево -> попадаем в `Root`.
4. Индекс `Root (0)` не больше индекса `Node B (7)`. Стоп.
5. Проверяем ключ в `Root`: "A" == "A". **Найдено!**

![](C:\Users\ARTno\AppData\Roaming\marktext\images\2026-04-10-21-11-19-image.png)









Флаг `-g` в GCC (GNU Compiler Collection) означает генерацию **отладочной информации** (debugging information) в формате, понятном для отладчиков, например, GDB. Он расшифровывается как **g**enerate/debug (генерация/отладка). Использование `-g` позволяет отладчику сопоставлять машинный код с исходным кодом: видеть имена функций, переменных и номера строк. ![Уральское отделение РАН |](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAVFBMVEX///95eXmmpqZ7e3v9/f3AwMDz8/O2tranp6fu7u7o6Oi4uLirq6vv7++tra3g4ODS0tKVlZXJycnZ2dmFhYWNjY1SUlKfn59ubm7W1tbFxcVxcXE2XJYTAAAAi0lEQVQYlXXISxLCIBBF0Qfh1w2kgRiJuv99SkxFM/FU3ckFjNxC0IdQLSitVXKmXeZ2xzpplfT8oXXfoHipmdkMwtw0JrjgllBDqGlxHDEZl0CFASkO7P+NVmj0G2KFSCyfw5QHhiZ0jFqePg6+SdwHr7M9eG/7GJ1xyhjDRvMdoApVceXRt0ldvN6m1QevS8cMqgAAAABJRU5ErkJggg==)Уральское отделение РАН | +1

**Основные факты о флаге -g:**

- **Назначение:** Добавляет в объектные файлы и исполняемый файл информацию о символах (имена переменных, функций) и карту соответствия машинных инструкций строкам исходного кода.
- **Использование:** Опцию необходимо указывать как на этапе компиляции, так и на этапе компоновки (linking), чтобы вся информация попала в финальный исполняемый файл.
- **Уровни отладки:** GCC поддерживает уровни отладки `-g0` (без отладочной информации), `-g1`, `-g2` (по умолчанию) и `-g3` (максимальная информация, включая макросы).
- **Совместимость:** Обычно `-g` включает формат, наиболее подходящий для операционной системы (например, DWARF в Linux).
- **Отладка без оптимизации:** Часто используется в связке с отсутствием флагов оптимизации (например, `-O0`), чтобы отладчик не путался из-за измененного компилятором порядка инструкций. ![OpenNET](data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxETEhMSEhIQFhUREBUVDxcVEhYVExcQFxcXFhgWGBMYHSosGRolHR8TITEhJSkrLi4uGB8zODMsNygtLisBCgoKDg0OFRAQGi0gGh0tLS0tLSs3NystLS0tKystKystLS0rLS0tLTcrLTcrKy0rMC0tLjcrOC0tMi0tKysrK//AABEIAIAAgAMBIgACEQEDEQH/xAAbAAEAAwEBAQEAAAAAAAAAAAAAAwQFBgIBB//EADAQAAIBAgQCCAYDAQAAAAAAAAABAgMRBAUxQRJRIWFxgZGhscEyYoLR4fATInJC/8QAGAEBAQEBAQAAAAAAAAAAAAAAAAIBBAP/xAAcEQEBAQEBAQEBAQAAAAAAAAAAARECMQNBIRL/2gAMAwEAAhEDEQA/AP10AHg0AAAAAADOzHMuB8MUm976LqsZbJ6NEFHLcw/kumkpJX6NGi8Jd8AAGgAAAAAAAAAAAAA8VqijFyeiVzlqs3JtvVu7NbPcRpBdsvZfvUYx4fW/3GxLhazhJSWz8t0dTGSaTWjV12M5I3ckxF4uD1jp/l/n2Hy6/G1ogA90gAAAAAAGwAIZ4umtZx8U34IgnmtJbt9kX72M2C6fJySTb0Su+wzJ51HaEn2tL7lLF5nKa4bJJ6218Sb9OY3FbEVXOTk935bIiPrPhzW6oLOCr8E1LbSXY9SsBLlHXgwsLmzilGUeKysnezt7lyGc091Ndya9TpnfNRjRBVhmNJ/9rvuvUsQqxekovsafoVLKPQANAxM9m+NR24brrd30m2QYzCxqRs9V8L5MnubMHMMEmIouEnGWq9OaIjlzFgAAAAAAAAAAH0+E2Fw0qkuGPe9kubEmjQyKpLilG74eG/Y7r8myRYXDxpx4Y973b5kp1czJiAAFCvjcIqkbPVfC+X4Ocr0nGTjJdKOrK2Owcais+hr4X+7Hn3xpK5kHqrTcW4vVOzPJzrAAAAAAAkoUnKSitWwPuGw8py4Y9/JLmzpMJho048K73u2fMHhY042X1PdsnOnjj/KbQAFsAAAAFwOZzGd6s/8AVvDoKx6nK7b5u55OS3asABgAAAXMplarHruvFMpkuGnacXykn5m8+xldUADrSAAAAABBjp2pzfyvxfQTlHOp2pP5pJe/sZfKOeAPdKm5O0U2+o5FvBLQw85u0U36eJqYTJ96j+le7+xqwgkrJJJcj15+V/Wa5WtQlB2kmv3Z7kZ1tSmpK0kmusycXk+9N/S/Zjr52eGsgHqcGnZpprZnk8musoTvGL5xT8UeyplM70o9V15v2sWzrniAAGgAABXx2G/khw3s73XaWAZZox6GTO/95K3y6vva6DUo0IwVopL93ZIDJzJ4AAKAAARYjDxmrSSfLmuxmXVyWV/6yVuu9/JdJsgm8y+mosLQUIqK21fNkoBQAAD/2Q==)OpenNET +4

Пример команды:  
`gcc -g main.c -o myprogram` — компилирует `main.c` с отладочной информацией в файл `myprogram`.
