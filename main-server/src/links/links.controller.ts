import { Body, Controller, Post } from '@nestjs/common';
import { SendLinksMessageDto } from './dto/send-links-message.dto';
import { LinksKafkaProducerService } from './links.kafka-producer.service';
import { LinksService } from './links.service';

@Controller('links')
export class LinksController {
  constructor(
    private linksKafkaProducerService: LinksKafkaProducerService,
    private readonly linksService: LinksService,
  ) {}

  @Post('/send-message-kafka')
  sendMessage(@Body() sendLinksMessageDto: SendLinksMessageDto) {
    this.linksKafkaProducerService.sendMessage({
      topic: 'LINKS-YOUTUBE',
      message: sendLinksMessageDto,
    });

    return { res: 'ok' };
  }

  @Post('/send-message-axios')
  async createLinksInformation(
    @Body() sendLinksMessageDto: SendLinksMessageDto,
  ) {
    const result = await this.linksService.createLinksInformation({
      sendLinksMessageDto,
    });
    return result;
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
