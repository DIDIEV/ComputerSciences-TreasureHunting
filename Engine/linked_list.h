// =============================================================================
// Team: [Your Team Number] | Variant: Treasure Hunt | Semester: 2026-I
// Members: [Student 1], [Student 2], [Student 3]
// File: linked_list.h
// Description: Header for the singly linked list that records player movement.
// =============================================================================

#pragma once
#include <string>

// ---------------------------------------------------------------------------
// Node: one visited cell in the movement history
// ---------------------------------------------------------------------------
struct MovementNode {
    int row;            // Grid row  (0-indexed)
    int col;            // Grid col  (0-indexed)
    int step;           // Turn number when this cell was visited
    MovementNode* next;

    MovementNode(int r, int c, int step);
};

// ---------------------------------------------------------------------------
// MovementList: singly linked list, insertion at tail (O(1))
// ---------------------------------------------------------------------------
class MovementList {
public:
    MovementList();
    ~MovementList();

    void append(int row, int col, int step); // Add position at end
    void clear();                            // Free all nodes
    bool contains(int row, int col) const;   // Check if position visited
    int  getSize() const;
    MovementNode* getHead() const;

    std::string toJson() const;              // Serialize to JSON array
    void print() const;                      // Debug print

private:
    MovementNode* head;
    MovementNode* tail;
    int size;
};