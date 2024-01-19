import { Body, Controller, Post } from '@nestjs/common';
import { LinksKafkaService } from './links.kafka.service';
import { SendLinksMessageDto } from './dto/send-links-message.dto';

@Controller('links')
export class LinksController {
  constructor(private readonly linksKafkaService: LinksKafkaService) {}

  @Post('/send-message')
  async sendMessage(@Body() sendLinksMessageDto: SendLinksMessageDto) {
    this.linksKafkaService.sendMessage({
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
