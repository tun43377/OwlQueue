import os

import discord
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand

from ohq.models import QueueEntry


class Command(BaseCommand):
    help = "Run the OwlQueue Discord bot"

    def handle(self, *args, **options):
        token = os.environ.get("DISCORD_TOKEN")
        if not token:
            self.stderr.write("Set DISCORD_TOKEN first: export DISCORD_TOKEN=your-token")
            return

        intents = discord.Intents.default()
        intents.message_content = True
        client = discord.Client(intents=intents)
        tree = discord.app_commands.CommandTree(client)

        @client.event
        async def on_ready():
            await tree.sync()
            print(f"Logged in as {client.user}")

        @tree.command(name="join", description="Join the office hours queue")
        async def join(interaction: discord.Interaction, question: str):
            await sync_to_async(QueueEntry.objects.create)(
                name=interaction.user.display_name, question=question
            )
            position = await sync_to_async(
                QueueEntry.objects.filter(helped=False).count
            )()
            await interaction.response.send_message(
                f"You're #{position} in line. Question: {question}"
            )

        @tree.command(name="queue", description="Show the current queue")
        async def queue(interaction: discord.Interaction):
            entries = await sync_to_async(list)(QueueEntry.objects.filter(helped=False))
            if not entries:
                await interaction.response.send_message("The queue is empty.")
                return
            lines = [f"{i + 1}. {e.name} — {e.question}" for i, e in enumerate(entries)]
            await interaction.response.send_message("\n".join(lines))

        client.run(token)