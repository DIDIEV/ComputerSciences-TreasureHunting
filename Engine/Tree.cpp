#include "tree.h"
#include <iostream>
#include <algorithm>

TreasureNode::TreasureNode(int id, int val, int r, int c, const std::string& name)
    : treasureId(id), value(val), row(r), col(c),
      name(name), collected(false),
      left(nullptr), right(nullptr) {}

TreasureBST::TreasureBST() : root(nullptr), nodeCount(0) {}

TreasureBST::~TreasureBST() {
    destroyTree(root);
}

void TreasureBST::insert(int id, int value, int row, int col,
                          const std::string& name) {
    root = insertRec(root, id, value, row, col, name);
    ++nodeCount;
}

bool TreasureBST::collect(int id) {
    return collectRec(root, id);
}

TreasureNode* TreasureBST::findMaxUncollected() const {
    return findMaxUncollectedRec(root, nullptr);
}

TreasureNode* TreasureBST::findMinUncollected() const {
    return findMinUncollectedRec(root, nullptr);
}

int TreasureBST::countUncollected() const {
    return countUncollectedRec(root);
}

int TreasureBST::getNodeCount() const { return nodeCount; }

std::string TreasureBST::toJson() const {
    std::string json = "[";
    bool first = true;
    inOrderJson(root, json, first);
    json += "]";
    return json;
}

int TreasureBST::height() const { return heightRec(root); }

void TreasureBST::printInOrder() const {
    std::cout << "Treasure BST (in-order by value):" << std::endl;
    printInOrderRec(root);
}

TreasureNode* TreasureBST::insertRec(TreasureNode* node, int id, int value,
                                      int row, int col,
                                      const std::string& name) {
    if (node == nullptr)
        return new TreasureNode(id, value, row, col, name);

    if (value < node->value ||
        (value == node->value && id < node->treasureId)) {
        node->left  = insertRec(node->left,  id, value, row, col, name);
    } else {
        node->right = insertRec(node->right, id, value, row, col, name);
    }
    return node;
}

bool TreasureBST::collectRec(TreasureNode* node, int id) {
    if (node == nullptr) return false;
    if (node->treasureId == id) {
        node->collected = true;
        return true;
    }
    return collectRec(node->left, id) || collectRec(node->right, id);
}

TreasureNode* TreasureBST::findMaxUncollectedRec(TreasureNode* node,
                                                   TreasureNode* best) const {
    if (node == nullptr) return best;
    best = findMaxUncollectedRec(node->left, best);
    if (!node->collected) {
        if (best == nullptr || node->value > best->value) best = node;
    }
    best = findMaxUncollectedRec(node->right, best);
    return best;
}

TreasureNode* TreasureBST::findMinUncollectedRec(TreasureNode* node,
                                                   TreasureNode* best) const {
    if (node == nullptr) return best;
    best = findMinUncollectedRec(node->left, best);
    if (!node->collected) {
        if (best == nullptr || node->value < best->value) best = node;
    }
    best = findMinUncollectedRec(node->right, best);
    return best;
}

int TreasureBST::countUncollectedRec(TreasureNode* node) const {
    if (node == nullptr) return 0;
    int self = node->collected ? 0 : 1;
    return self + countUncollectedRec(node->left)
                + countUncollectedRec(node->right);
}

int TreasureBST::heightRec(TreasureNode* node) const {
    if (node == nullptr) return 0;
    return 1 + std::max(heightRec(node->left), heightRec(node->right));
}

void TreasureBST::inOrderJson(TreasureNode* node, std::string& json,
                               bool& first) const {
    if (node == nullptr) return;
    inOrderJson(node->left, json, first);
    if (!first) json += ",";
    // Escape the name string for safety
    std::string safeName = node->name;
    for (size_t i = 0; i < safeName.size(); ++i)
        if (safeName[i] == '"') safeName.replace(i, 1, "\\\"");

    json += "{\"id\":"        + std::to_string(node->treasureId) +
            ",\"value\":"     + std::to_string(node->value)      +
            ",\"row\":"       + std::to_string(node->row)        +
            ",\"col\":"       + std::to_string(node->col)        +
            ",\"name\":\""    + safeName                         + "\"" +
            ",\"collected\":" + (node->collected ? "true" : "false") + "}";
    first = false;
    inOrderJson(node->right, json, first);
}

void TreasureBST::printInOrderRec(TreasureNode* node) const {
    if (node == nullptr) return;
    printInOrderRec(node->left);
    std::cout << "  [id=" << node->treasureId
              << " val=" << node->value
              << " pos=(" << node->row << "," << node->col << ")"
              << " name=" << node->name
              << " collected=" << (node->collected ? "yes" : "no")
              << "]" << std::endl;
    printInOrderRec(node->right);
}

void TreasureBST::destroyTree(TreasureNode* node) {
    if (node == nullptr) return;
    destroyTree(node->left);
    destroyTree(node->right);
    delete node;
}