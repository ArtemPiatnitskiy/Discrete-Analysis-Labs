// #include <algorithm>
#include <cctype>
#include <cstddef>
#include <ostream>
#include <fstream>
#include <cerrno>
#include <cstring>
#include <iostream>
#include <string>
#include <cstdint>
#include <type_traits>



template<typename T>
concept Scalar = std::is_scalar_v<T>;

template<Scalar T>
class Node {

    private:
        std::string key;
        T value;
        size_t index;

        Node* left = nullptr;
        Node* right = nullptr;

    public:
        Node(const std::string& key, const T& value, const size_t& index) 
        : key(key), value(value), index(index) {}

        // Стандартный деструктор
        ~Node() = default;

        const std::string& get_key() {
            return key;
        }

        T& get_value() {
            return value;
        }

        const T& get_value() const {
            return value;
        }

        size_t get_index() {return index;}

        void set_value(const T& new_value) {
            value = new_value;
        }

        void set_key(const std::string& new_key) {
            key = new_key;
        }

        void set_left(Node<T>* node) {
            left = node;
        }

        void set_right(Node<T>* node) {
            right = node;
        }

        Node<T>* get_left() {return left;}

        Node<T>* get_right() {return right;}


};

template<Scalar T>
class Patricia {
    private:
        Node<T>* root = nullptr;

        uint8_t get_bit(const std::string& key, size_t index) {
            if (index == 0) return 0;

            size_t byte_index = (index - 1) / 8;

            if(byte_index >= key.length()) return 0;

            uint8_t mask = 1;

            uint8_t byte = key[byte_index];
            // Считаем, что мы идём по байту слева направо, тогда наши индексы будут располагаться так:
            // 11111111 -> 01234567, где 0 - самый старший бит, а 7 - самый младший
            mask = (1 << (7 - (index - 1) % 8));

            return ((byte & mask) == 0 ? 0 : 1);
        }

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


        void search_target_q(const std::string& key, Node<T>*& Target, Node<T>*& q, Node<T>*& parent_q) {
            Target = root->get_left();
            q = root;
            parent_q = nullptr;

            while (Target->get_index() > q->get_index()) {
                parent_q = q;
                q = Target;
                uint8_t bit = get_bit(key, Target->get_index());
                Target = (bit == 0) ? Target->get_left() : Target->get_right();
            }

            if (key == Target->get_key()) return;
            // Если ключи не совпали, то значит, что такого элемента нет в дереве
            else {
                Target = nullptr;
                q = nullptr;
                parent_q = nullptr;
                return;
            }
        }


        void cleanNode(Node<T>* node) {
            if (node->get_left() && node->get_left()->get_index() > node->get_index()) {
                cleanNode(node->get_left());
            }
            if (node->get_right() && node->get_right()->get_index() > node->get_index()) {
                cleanNode(node->get_right());
            }
            delete node;
        }


        void Save_node(std::ofstream& out, Node<T>* node) {
            if (node == nullptr) return;

            size_t key_size = node->get_key().size();
            out.write(reinterpret_cast<const char*>(&key_size), sizeof(key_size));
            out.write(node->get_key().c_str(), key_size);
            out.write(reinterpret_cast<const char*>(&node->get_value()), sizeof(T));

            if (node->get_left() && node->get_left()->get_index() > node->get_index()) {
                Save_node(out, node->get_left());
            }
            if (node->get_right() && node->get_right()->get_index() > node->get_index()) {
                Save_node(out, node->get_right());
            }
        }




    public:
        Patricia() = default;

        Patricia(std::string& key, T& data) {
            root = new Node(key, data, 0);

            root->set_left(root);
            root->set_right(nullptr);
        }

        ~Patricia() {
            if (root == nullptr) return;
            if (root != root->get_left()) {
                cleanNode(root->get_left());
            }
            delete root;
            root = nullptr;
        }


        bool insert(const std::string& key, const T& data) {
            if (root == nullptr) {
                root = new Node<T>(key, data, 0);
                root->set_left(root);   
                return true;
            }

            Node<T>* prev = root;
            Node<T>* current = root->get_left();

            while(current->get_index() > prev->get_index()) {
                prev = current;
                uint8_t bit = get_bit(key, current->get_index());

                current = (bit == 0) ? current->get_left() : current->get_right();
            }

            if (key == current->get_key()) {
                return false;
            }


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

            return true;
        }

        T* search(const std::string& key) {
            if (root == nullptr) return nullptr;

            Node<T>* current = root->get_left();
            Node<T>* prev = root;

            while (current->get_index() > prev->get_index()) {
                prev = current;

                uint8_t bit = get_bit(key, current->get_index());
                current = bit == 0 ? current->get_left() : current->get_right();
            }
            if (key == current->get_key()) {
                return &(current->get_value());
            } 
            else {
                return nullptr;
            }
        }

        bool remove(const std::string& key) {
            if (root == nullptr) return false;

            // Удаляем корень без ничего
            if (key == root->get_key() && root->get_left() == root) {
                delete root;
                root = nullptr;
                return true;
            }

            // Случай 1. Удаляем элемент, который имеет обратную ссылку на себя
            Node<T>* Target = nullptr;
            Node<T>* q = nullptr;
            Node<T>* parent_q = nullptr;
            search_target_q(key, Target, q, parent_q);

            if (Target == nullptr) return false;
            
            if (Target == q && Target != root) {
                Node<T>* child = nullptr;

                if (Target->get_left() == Target) child = Target->get_right();
                else if (Target->get_right() == Target) child = Target->get_left();

                if (child != nullptr) {
                    uint8_t bit = get_bit(key, parent_q->get_index());
                    if (bit == 0) parent_q->set_left(child);
                    else parent_q->set_right(child);
                    delete Target;
                    return true;
                }
            }

            // Случай 2. Удаляем элемент, который не имеет обратной ссылки на себя
            Node<T>* tempTg = nullptr;
            Node<T>* q_back = nullptr;
            Node<T>* tempPr = nullptr;
            Node<T>* child_q = nullptr;
            search_target_q(q->get_key(), tempTg, q_back, tempPr);
            if (Target == q->get_left()) child_q = q->get_right();
            else child_q = q->get_left();

            if (child_q == q) {
                child_q = Target;
            }

            if (parent_q != nullptr) {
                uint8_t bit = get_bit(key, parent_q->get_index());
                if (bit == 0) parent_q->set_left(child_q);
                else parent_q->set_right(child_q);
            }
            else {
                root->set_left(child_q);
            }
            
            if (q_back != nullptr && q_back != q) {
                uint8_t bit = get_bit(q->get_key(), q_back->get_index());
                if (bit == 0) q_back->set_left(Target);
                else q_back->set_right(Target);
            }
            Target->set_value(q->get_value());
            Target->set_key(q->get_key());
            delete q;
            return true;

        }

        int Save_to_file(const std::string& path_to_file) {
            std::ofstream out(path_to_file, std::ios::binary);
            if (!out.is_open()) {
                std::cerr << "ERROR: " << std::strerror(errno) << '\n';
                return -1;
            }
            else {
                if (root != nullptr) {
                    Save_node(out, root->get_left());
                }
            }
            return 0;
        }

        int load_from_file(const std::string& path_to_file) {
            std::ifstream in(path_to_file, std::ios::binary);
            if (!in.is_open()) {
                std::cerr << "ERROR: " << std::strerror(errno) << '\n';
                return -1;
            }
            Patricia<T> temp;
            size_t len;

            while (in.read(reinterpret_cast<char*>(&len), sizeof(len))) {

                if (len > 256) {
                    std::cerr << "ERROR: Invalid format key. Key length must be <= 256.\n";
                    return -1;
                }

                std::string key(len, '\n');
                T value;
                
                if (!in.read(key.data(), len)) return -1;
                if (!in.read(reinterpret_cast<char*>(&value), sizeof(T))) return -1;
                temp.insert(key, value);
            }
            std::swap(root, temp.root);
            return 0;
            
        }

        

};


void string_to_lower(std::string& str) {
    for (auto& ch : str) {
        ch = std::tolower(static_cast<unsigned char>(ch));
    }
}



int main() {

    std::ios_base::sync_with_stdio(false);
    std::cin.tie(NULL);
    
    Patricia<uint64_t> patricia;

    std::string command;

    while (std::cin >> command) {
        try {
            if (command == "+") {
                std::string key;
                uint64_t value;
                std::cin >> key >> value;
                string_to_lower(key);
                if (patricia.insert(key, value)) {
                    std::cout << "OK\n";
                }
                else {
                    std::cout << "Exist\n";
                }
            }
            else if (command == "-") {
                std::string key;
                std::cin >> key;
                string_to_lower(key);
                if (patricia.remove(key)) {
                    std::cout << "OK\n";
                }
                else {
                    std::cout << "NoSuchWord\n";
                }
            }
            else if (command == "!") {
                std::string subcommand, path;
                std::cin >> subcommand >> path;
                if (subcommand == "Save") {
                    if (patricia.Save_to_file(path) == 0) {
                        std::cout << "OK\n";
                    }
                }
                else if (subcommand == "Load") {
                    if (patricia.load_from_file(path) == 0) {
                        std::cout << "OK\n";
                    }
                }
            }
            else {
                string_to_lower(command);
                uint64_t* value = patricia.search(command);
                if (value != nullptr) {
                    std::cout << "OK: " << *value << '\n';
                }
                else {
                    std::cout << "NoSuchWord\n";
                }
            }
        } catch (const std::bad_alloc& e) {
            std::cout << "ERROR: Mem alloc failed\n";
        } catch (const std::exception& e) {
            std::cout << "ERROR: " << e.what() << '\n';
        }
    }
}
