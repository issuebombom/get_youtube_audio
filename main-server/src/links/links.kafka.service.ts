import { Inject, Injectable } from '@nestjs/common';
import { Consumer, Producer } from 'kafkajs';

@Injectable()
export class LinksKafkaService {
  constructor(
    @Inject('KafkaProducer') private readonly producer: Producer,
    @Inject('KafkaConsumer') private readonly consumer: Consumer,
  ) {
    // this.producer.connect(); // 여기서 하면 안됨 함수에서 커넥션 해야함
    // this.consumer.connect();
    // this.consumer.subscribe({topics: ['TEST-A']})
  }

  async sendMessage({
    topic,
    message,
  }: ILinksKafkaServiceSendMessage): Promise<void> {
    await this.producer.connect();
    await this.producer.send({
      topic,
      messages: [{ value: JSON.stringify(message) }],
    });
    await this.producer.disconnect();
  }
}

interface ILinksKafkaServiceSendMessage {
  topic: string;
  message: Record<string, any>;
}
