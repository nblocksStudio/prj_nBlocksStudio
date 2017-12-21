#include "fifo.h"

fifo::fifo()
{
    this->head = 0;
    this->tail = 0;
}
uint32_t fifo::available()
{
    return (FIFO_SIZE + this->head - this->tail) % FIFO_SIZE;
}
uint32_t fifo::free()
{
    return (FIFO_SIZE - 1 - available());
}
uint8_t fifo::put(FIFO_TYPE data)
{
    uint32_t next;

    // check if FIFO has room
    next = (this->head + 1) % FIFO_SIZE;
    if (next == this->tail)
    {
        // full
        return 1;
    }

    this->buffer[this->head] = data;
    this->head = next;

    return 0;
}
uint8_t fifo::read(FIFO_TYPE* data)
{
    // check if FIFO has data
    if (this->head == this->tail)
    {
        return 1; // FIFO empty
    }

    *data = this->buffer[this->tail];

    return 0;
}
uint8_t fifo::get(FIFO_TYPE* data)
{
    uint32_t next;

    // check if FIFO has data
    if (this->head == this->tail)
    {
        return 1; // FIFO empty
    }

    next = (this->tail + 1) % FIFO_SIZE;

    *data = this->buffer[this->tail];
    this->tail = next;

    return 0;
}

