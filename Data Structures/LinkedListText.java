package editor;

public class LinkedListText<Item> {
    public class Node {
        public Node prev;
        public Item item;
        public Node next;

        public Node(Node g, Item i, Node h) {
            prev= g;
            item= i;
            next= h;

        }
        public void addNode(Item a) {
            Node temp = next;
            next = new Node(this, a, temp);
            next.next.prev = next;
        }
        public void reAddNode(Node c) {
            Node b = next;
            next = c;
            next.next = b;
            next.next.prev = c;
        }
        public Item removeNode() {
            Item temp = next.item;
            next = next.next;
            next.prev = next.prev.prev;
            return temp;
        }

    }
    private Node sentinel;
    private int size;
    public LinkedListText(Item a) {
        size = 0;
        sentinel = new Node(null, a, null);
        sentinel.prev=sentinel;
        sentinel.next=sentinel;
    }
    public Node getSentinel() {
        return sentinel;
    }
}