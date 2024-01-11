import { Inject, Injectable } from '@nestjs/common';
import { ClientKafka } from '@nestjs/microservices';
import { SendLinksMessageDto } from './dto/send-links-message.dto';

@Injectable()
export class LinksKafkaProducerService {
  constructor(
    @Inject('YOUTUBE_SERVICE') private readonly clientKafka: ClientKafka,
  ) {}

  sendMessage({ topic, message }: ILinksKafkaProducerServiceSendMessage): void {
    const jsonString = JSON.stringify(message)
    this.clientKafka.emit<SendLinksMessageDto>(topic, jsonString);
  }
}

interface ILinksKafkaProducerServiceSendMessage {
  topic: string;
  message: Record<string, any>;
}
