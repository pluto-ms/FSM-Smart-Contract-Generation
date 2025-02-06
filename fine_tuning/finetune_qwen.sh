NCCL_P2P_DISABLE=1 \
NCCL_IB_DISABLE=1 \
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 \
torchrun \
--nproc_per_node 8 \
--nnodes 1 \
--node_rank 0 \
--master_addr localhost \
--master_port 6600 \
./finetune_qwen.py \
--model_name_or_path "../models/Qwen/Qwen2___5-7B-Instruct/" \
--data_path "../data/q_to_fsm_to_code.json" \
--fp16 True \
--output_dir "./output/qwen/qwen2.5_7B_full" \
--num_train_epochs 3 \
--per_device_train_batch_size 2 \
--per_device_eval_batch_size 2 \
--gradient_accumulation_steps 8 \
--eval_strategy "no" \
--save_strategy "steps" \
--save_steps 20 \
--save_total_limit 50 \
--learning_rate 5e-5 \
--weight_decay 0.1 \
--adam_beta2 0.95 \
--warmup_ratio 0.01 \
--lr_scheduler_type "cosine" \
--logging_steps 1 \
--report_to "none" \
--model_max_length 2048 \
--gradient_checkpointing True \
--lazy_preprocess True \
--deepspeed "./config/ds_config_zero2.json"