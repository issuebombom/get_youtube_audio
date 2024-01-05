import { Body, Controller, Post } from '@nestjs/common';
import { LinksKafkaProducerService } from './links.kafka-producer.service';
import { SendLinksMessageDto } from './dto/send-links-message.dto';

@Controller('links')
export class LinksController {
  constructor(
    private readonly linksKafkaProducerService: LinksKafkaProducerService,
  ) {}

  @Post('/send-message')
  sendMessage(@Body() sendLinksMessageDto: SendLinksMessageDto) {
    this.linksKafkaProducerService.sendMessage({
      topic: 'TEST-KAFKA',
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
