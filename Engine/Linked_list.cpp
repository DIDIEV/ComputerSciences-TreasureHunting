
#include "linked_list.h"
#include <iostream>

MovementNode::MovementNode(int r, int c, int step)
    : row(r), col(c), step(step), next(nullptr) {}

MovementList::MovementList() : head(nullptr), tail(nullptr), size(0) {}

MovementList::~MovementList() {
    clear();
}

void MovementList::append(int row, int col, int step) {
    MovementNode* node = new MovementNode(row, col, step);
    if (tail == nullptr) {
        head = tail = node;
    } else {
        tail->next = node;
        tail = node;
    }
    ++size;
}

void MovementList::clear() {
    MovementNode* current = head;
    while (current != nullptr) {
        MovementNode* next = current->next;
        delete current;
        current = next;
    }
    head = tail = nullptr;
    size = 0;
}

bool MovementList::contains(int row, int col) const {
    MovementNode* current = head;
    while (current != nullptr) {
        if (current->row == row && current->col == col) return true;
        current = current->next;
    }
    return false;
}

int MovementList::getSize() const { return size; }
MovementNode* MovementList::getHead() const { return head; }

std::string MovementList::toJson() const {
    std::string json = "[";
    MovementNode* current = head;
    bool first = true;
    while (current != nullptr) {
        if (!first) json += ",";
        json += "{\"row\":" + std::to_string(current->row) +
                ",\"col\":"  + std::to_string(current->col) +
                ",\"step\":" + std::to_string(current->step) + "}";
        first = false;
        current = current->next;
    }
    json += "]";
    return json;
}

void MovementList::print() const {
    MovementNode* current = head;
    std::cout << "Movement history (" << size << " steps):" << std::endl;
    while (current != nullptr) {
        std::cout << "  step " << current->step
                  << " -> (" << current->row << "," << current->col << ")"
                  << std::endl;
        current = current->next;
    }
}