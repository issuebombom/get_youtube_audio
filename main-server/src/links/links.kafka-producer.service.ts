import { Inject, Injectable } from '@nestjs/common';
import { ClientKafka } from '@nestjs/microservices';
import { SendLinksMessageDto } from './dto/send-links-message.dto';

@Injectable()
export class LinksKafkaProducerService {
  constructor(
    @Inject('LINK_SERVICE') private readonly kafkaProducer: ClientKafka,
  ) {}

  sendMessage({ topic, message }: ILinksKafkaProducerServiceSendMessage): void {
    this.kafkaProducer.emit<SendLinksMessageDto>(
      topic,
      JSON.stringify(message),
    );
  }
}

interface ILinksKafkaProducerServiceSendMessage {
  topic: string;
  message: Record<string, any>;
}
