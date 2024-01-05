import { Injectable } from '@nestjs/common';
import { EachMessagePayload, Kafka } from 'kafkajs';

@Injectable()
export class LinksService {
  private kafka = new Kafka({
    clientId: 'test-client-0',
    brokers: ['localhost:9092'],
  });
  private producer = this.kafka.producer();
  private consumer = this.kafka.consumer({ groupId: 'test-group-0' });

  constructor() {
    this.producer.connect();

    this.consumer.connect();
    this.consumer.subscribe({ topics: ['test_a'] });
    // this.consumer.run({
    //   eachMessage: this.consumerCallback, //메세지 수신 콜백
    // });
  }

  async sendLinksProducer(getLinksInformationDto: { urls: string }) {
    const { urls } = getLinksInformationDto;
    await this.producer.send({
      topic: 'test-topic',
      messages: [{ value: urls }],
    });

    await this.producer.disconnect();
  }

  // async consumerCallback(payload: EachMessagePayload) {
  //   //메세지 수신 콜백
  //   console.log('kafka message arrived');
  //   console.log(
  //     `topic: ${payload.topic}, Message:${payload.message.value.toString()}`,
  //   );
  // }
}
