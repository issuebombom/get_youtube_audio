import { Body, Controller, Post } from '@nestjs/common';
import { SendLinksMessageDto } from './dto/send-links-message.dto';
import { LinksKafkaProducerService } from './links.kafka-producer.service';

@Controller('links')
export class LinksController {
  constructor(private readonly linksKafkaProducerService: LinksKafkaProducerService) {}

  @Post('/send-message')
  async sendMessage(@Body() sendLinksMessageDto: SendLinksMessageDto) {
    this.linksKafkaProducerService.sendMessage({
      topic: 'LINKS-YOUTUBE',
      message: sendLinksMessageDto,
    });

    return sendLinksMessageDto;
  }
}

// @MessagePattern('get-links-msg')
// getLinksInformation(
//   @Payload() message: string,
//   @Ctx() context: KafkaContext,
// ) {
//   const OriginalMessage = context.getMessage();
//   const res = OriginalMessage.value;
//   console.log(message, res);
// }
