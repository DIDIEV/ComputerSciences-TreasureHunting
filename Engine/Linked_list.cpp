// =============================================================================
// Team: [Your Team Number] | Variant: Treasure Hunt | Semester: 2026-I
// Members: [Student 1], [Student 2], [Student 3]
// File: linked_list.cpp
// Description: Singly linked list implementation for movement history tracking.
//              Stores every cell the player has visited during the game session.
// =============================================================================

#include "linked_list.h"
#include <iostream>

// ---------------------------------------------------------------------------
// Node
// ---------------------------------------------------------------------------

MovementNode::MovementNode(int r, int c, int step)
    : row(r), col(c), step(step), next(nullptr) {}

// ---------------------------------------------------------------------------
// MovementList
// ---------------------------------------------------------------------------

MovementList::MovementList() : head(nullptr), tail(nullptr), size(0) {}

MovementList::~MovementList() {
    clear();
}

// Append a new position at the end of the list — O(1) via tail pointer
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

// Remove all nodes and reset the list — O(n)
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

// Check if the player has already visited (row, col) — O(n)
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

// Serialize the full list to a JSON array for state.json output — O(n)
// Format: [{"row":r,"col":c,"step":s}, ...]
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

// Debug helper — prints the full history to stdout
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